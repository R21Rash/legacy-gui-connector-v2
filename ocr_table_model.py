
import os
import json
import glob
import re
import math
import argparse
import shutil
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import cv2
import numpy as np
import pytesseract


# ------------------------- Tesseract Path Auto-Detect -------------------------
def _ensure_tesseract_path():
    # 1) Use env var if provided
    env_path = os.environ.get("TESSERACT_PATH")
    if env_path and os.path.isfile(env_path):
        pytesseract.pytesseract.tesseract_cmd = env_path
        return

    # 2) If tesseract is on PATH, use it
    found = shutil.which("tesseract")
    if found:
        pytesseract.pytesseract.tesseract_cmd = found
        return

    # 3) Common Windows locations
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            pytesseract.pytesseract.tesseract_cmd = c
            return

    # Otherwise, let pytesseract raise a helpful error later
_ensure_tesseract_path()


# ------------------------------ Config / Aliases ------------------------------
EXPECTED_HEADERS = [
    {"name": "Patient_ID",     "aliases": ["patient_id", "patient id", "id"]},
    {"name": "Patient_Name",   "aliases": ["patient_name", "patient name", "name"]},
    {"name": "Address",        "aliases": ["address"]},
    {"name": "Date_Of_Birth",  "aliases": ["date_of_birth", "date of birth", "dob", "d.o.b"]},
    {"name": "Age",            "aliases": ["age"]},
    {"name": "Sex",            "aliases": ["sex", "gender", "m/f"]},
]

DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")


# --------------------------------- Utilities ----------------------------------
def imread_gray(path: str) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise RuntimeError(f"Failed to read image: {path}")
    return img


def deskew(img: np.ndarray) -> np.ndarray:
    # Otsu threshold → invert so text is white for skew detection
    thr = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    thr = cv2.bitwise_not(thr)
    coords = np.column_stack(np.where(thr > 0))
    angle = 0.0
    if coords.size > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def preprocess(img: np.ndarray, scale: float = 1.8) -> np.ndarray:
    img = deskew(img)
    if scale != 1.0:
        img = cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    # Denoise + sharpen
    img = cv2.bilateralFilter(img, 7, 25, 25)
    blur = cv2.GaussianBlur(img, (0, 0), 1.0)
    img = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    # Adaptive threshold → white bg, black text
    bin_img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    return bin_img


def tsv(img_bin: np.ndarray, psm=6) -> List[Dict]:
    config = f"--oem 3 --psm {psm}"
    data = pytesseract.image_to_data(img_bin, config=config, output_type=pytesseract.Output.DICT)
    n = len(data["text"])
    items = []
    for i in range(n):
        text = data["text"][i]
        if text is None or str(text).strip() == "" or int(data["conf"][i]) < 0:
            continue
        left = int(data["left"][i]); top = int(data["top"][i])
        width = int(data["width"][i]); height = int(data["height"][i])
        right = left + width; bottom = top + height
        items.append({
            "text": str(text),
            "conf": float(data["conf"][i]),
            "left": left, "top": top, "width": width, "height": height,
            "right": right, "bottom": bottom,
            "cx": left + width / 2.0, "cy": top + height / 2.0,
        })
    return items


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def header_match(tok: str) -> Optional[str]:
    t = norm(tok)
    for h in EXPECTED_HEADERS:
        if t == norm(h["name"]):
            return h["name"]
        for a in h["aliases"]:
            if t == norm(a):
                return h["name"]
    return None


@dataclass
class Template:
    columns: List[Tuple[str, float]]   # [(col_name, x_center), ...] sorted by x
    x_cuts: List[float]                # [x1, x2, ...] between columns
    header_bottom_y: float             # Y below headers

    def to_dict(self) -> Dict:
        return {
            "columns": self.columns,
            "x_cuts": self.x_cuts,
            "header_bottom_y": self.header_bottom_y,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Template":
        return Template(
            columns=[(str(name), float(x)) for name, x in d["columns"]],
            x_cuts=[float(x) for x in d["x_cuts"]],
            header_bottom_y=float(d["header_bottom_y"]),
        )


# ------------------------------ Learn Template -------------------------------
def _merge_header_tokens(header_items_sorted: List[Dict]) -> List[Dict]:
    merged: List[Dict] = []
    for it in header_items_sorted:
        if not merged:
            merged.append(it.copy())
            continue
        prev = merged[-1]
        # Same line?
        same_line = abs(it["cy"] - prev["cy"]) < max(prev["height"], it["height"]) * 0.7
        # Close in X?
        close_x = (it["left"] - prev["right"]) < max(prev["height"], it["height"]) * 1.3
        if same_line and close_x:
            prev["text"] = (prev["text"] + " " + it["text"]).strip()
            prev["right"] = it["right"]
            prev["width"] = prev["right"] - prev["left"]
            prev["cx"] = prev["left"] + prev["width"] / 2.0
            prev["cy"] = (prev["cy"] + it["cy"]) / 2.0
            prev["bottom"] = max(prev["bottom"], it["bottom"])
        else:
            merged.append(it.copy())
    return merged


def learn_template_from_folder(folder: str, psm: int = 6, debug: bool = False, outdir: Optional[str] = None) -> Template:
    paths = sorted(
        [p for p in glob.glob(os.path.join(folder, "*.*")) if p.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"))]
    )
    if not paths:
        raise RuntimeError(f"No images found in: {folder}")

    header_hits: Dict[str, List[float]] = {h["name"]: [] for h in EXPECTED_HEADERS}
    header_bottoms: List[float] = []

    if outdir:
        os.makedirs(outdir, exist_ok=True)

    for p in paths:
        img = imread_gray(p)
        bin_img = preprocess(img, scale=1.8)
        items = tsv(bin_img, psm=psm)
        if not items:
            continue

        H, W = bin_img.shape[:2]
        header_limit = H * 0.45
        header_items = [it for it in items if it["cy"] < header_limit]
        header_items_sorted = sorted(header_items, key=lambda x: (x["cy"], x["cx"]))
        merged = _merge_header_tokens(header_items_sorted)

        for m in merged:
            # Attempt to normalize underscores vs spaces
            candidate = m["text"].replace("_", " ")
            col_name = header_match(candidate)
            if col_name:
                header_hits[col_name].append(m["cx"])
                header_bottoms.append(m["bottom"])

        if debug and outdir:
            # Draw merged header boxes for QA
            dbg = cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR)
            for m in merged:
                cv2.rectangle(dbg, (int(m["left"]), int(m["top"])), (int(m["right"]), int(m["bottom"])), (0, 0, 255), 2)
                cv2.putText(dbg, m["text"], (int(m["left"]), max(15, int(m["top"]) - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1, cv2.LINE_AA)
            cv2.imwrite(os.path.join(outdir, f"debug_headers_{os.path.basename(p)}"), dbg)

    # Build columns list from medians
    cols: List[Tuple[str, float]] = []
    for h in EXPECTED_HEADERS:
        name = h["name"]
        xs = header_hits[name]
        if xs:
            xs_sorted = sorted(xs)
            median_x = xs_sorted[len(xs_sorted) // 2]
            cols.append((name, median_x))

    if len(cols) < 3:
        raise RuntimeError("Not enough headers recognized to learn a template. Improve OCR or header aliases.")

    cols.sort(key=lambda x: x[1])
    x_cuts = [ (cols[i][1] + cols[i+1][1]) / 2.0 for i in range(len(cols) - 1) ]
    header_bottom_y = sorted(header_bottoms)[len(header_bottoms) // 2] if header_bottoms else 0.0

    if debug and outdir:
        # Create a simple visual of x cuts
        vis = np.full((400, int(cols[-1][1] + 100)), 255, dtype=np.uint8)
        for name, x in cols:
            cv2.line(vis, (int(x), 0), (int(x), 399), 200, 1)
            cv2.putText(vis, name, (int(x) - 40, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, cv2.LINE_AA)
        for xc in x_cuts:
            cv2.line(vis, (int(xc), 0), (int(xc), 399), 0, 1)
        cv2.imwrite(os.path.join(outdir, "debug_template_xcuts.png"), vis)

    return Template(columns=cols, x_cuts=x_cuts, header_bottom_y=header_bottom_y)


# ------------------------------- Parse with Template --------------------------
def assign_column(x: float, template: Template) -> str:
    for i, cut in enumerate(template.x_cuts):
        if x < cut:
            return template.columns[i][0]
    return template.columns[-1][0]


def group_rows(items: List[Dict], start_y: float) -> List[List[Dict]]:
    # Ignore header region
    body = [it for it in items if it["cy"] > start_y + 2]
    if not body:
        return []
    body.sort(key=lambda it: it["cy"])
    rows: List[List[Dict]] = []
    current: List[Dict] = []
    avg_h = np.median([it["height"] for it in body])
    y_tol = max(10.0, avg_h * 0.7)

    last_y = None
    for it in body:
        if last_y is None:
            current = [it]; last_y = it["cy"]; continue
        if abs(it["cy"] - last_y) <= y_tol:
            current.append(it)
            last_y = (last_y + it["cy"]) / 2.0
        else:
            rows.append(sorted(current, key=lambda x: x["cx"]))
            current = [it]; last_y = it["cy"]
    if current:
        rows.append(sorted(current, key=lambda x: x["cx"]))
    return rows


def clean_cell(col: str, text: str) -> str:
    s = " ".join(text.split())
    if col == "Patient_ID":
        s = re.sub(r"[^\d]", "", s)
    if col in ("Age",):
        m = re.search(r"\b(\d{1,3})\b", s)
        s = m.group(1) if m else s
    if col == "Date_Of_Birth":
        m = DATE_RE.search(s)
        s = m.group(0) if m else s
    return s


def postprocess_row(row: Dict[str, str]) -> Dict[str, str]:
    # If Age/Sex merged into one cell, try to split
    if (not row.get("Sex")) and row.get("Age"):
        parts = row["Age"].split()
        if len(parts) >= 2:
            if re.fullmatch(r"\d{1,3}", parts[0]) and re.fullmatch(r"[A-Za-z]+", parts[-1]):
                row["Age"] = parts[0]
                row["Sex"] = parts[-1]
    return row


def parse_image_with_template(path: str, template: Template, psm: int = 6, debug: bool = False, outdir: Optional[str] = None) -> List[Dict]:
    img = imread_gray(path)
    bin_img = preprocess(img, scale=1.8)
    items = tsv(bin_img, psm=psm)
    if not items:
        return []

    rows = group_rows(items, start_y=template.header_bottom_y)

    col_names = [c[0] for c in template.columns]
    parsed_rows: List[Dict] = []

    for r in rows:
        cells: Dict[str, List[str]] = {name: [] for name in col_names}
        for w in r:
            col = assign_column(w["cx"], template)
            cells[col].append(w["text"])
        row_out = {name: clean_cell(name, " ".join(cells[name]).strip()) for name in col_names}
        row_out = postprocess_row(row_out)
        if any(v for v in row_out.values()):
            parsed_rows.append(row_out)

    if debug and outdir:
        # Save a quick overlay of rows for QA
        dbg = cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR)
        for r in rows:
            ys = [w["top"] for w in r] + [w["bottom"] for w in r]
            y1, y2 = min(ys), max(ys)
            cv2.rectangle(dbg, (0, int(y1)), (dbg.shape[1]-1, int(y2)), (0, 255, 0), 1)
        cv2.imwrite(os.path.join(outdir, f"debug_rows_{os.path.basename(path)}"), dbg)

    return parsed_rows


# ------------------------------------ CLI -------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Mini OCR table model: learn a layout once, parse many images.")
    ap.add_argument("--learn", type=str, help="Folder with training images (same layout).")
    ap.add_argument("--parse", type=str, help="Folder with images to parse.")
    ap.add_argument("--template", type=str, help="Path to template.json (required for --parse unless also doing --learn).")
    ap.add_argument("--save-template", type=str, default="template.json", help="Where to save learned template.")
    ap.add_argument("--out", type=str, default="rows.json", help="Where to save parsed JSON rows.")
    ap.add_argument("--psm", type=int, default=6, help="Tesseract page segmentation mode (default 6).")
    ap.add_argument("--debug", action="store_true", help="Save debug overlays.")
    ap.add_argument("--outdir", type=str, default="_ocr_debug", help="Debug output folder if --debug is set.")
    args = ap.parse_args()

    tpl: Optional[Template] = None

    if args.learn:
        tpl = learn_template_from_folder(args.learn, psm=args.psm, debug=args.debug, outdir=args.outdir if args.debug else None)
        with open(args.save_template, "w", encoding="utf-8") as f:
            json.dump(tpl.to_dict(), f, indent=2)
        print(f"[ok] Template learned and saved → {args.save_template}")
        if not args.parse:
            return

    if args.parse:
        if tpl is None:
            if not args.template:
                raise SystemExit("Provide --template (or run --learn at the same time).")
            with open(args.template, "r", encoding="utf-8") as f:
                tpl = Template.from_dict(json.load(f))

        all_rows: List[Dict] = []
        paths = sorted(
            [p for p in glob.glob(os.path.join(args.parse, "*.*")) if p.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"))]
        )
        if not paths:
            print(f"[warn] No images found in {args.parse}")
        for p in paths:
            rows = parse_image_with_template(p, tpl, psm=args.psm, debug=args.debug, outdir=args.outdir if args.debug else None)
            all_rows.extend(rows)

        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"[ok] Parsed {len(all_rows)} rows → {args.out}")


if __name__ == "__main__":
    main()
