import json
import os
import subprocess
import sys

# --- CONFIG: update ONLY if your paths are different ---
AHK_EXE_DEFAULT = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"
AGENT3_AHK_DEFAULT = os.path.join(os.path.dirname(__file__), "agent3.ahk")  # <-- the .ahk script in this folder
CALIB_JSON = os.path.join(os.path.dirname(__file__), "calibration.json")
PAYLOAD_INI = os.path.join(os.path.dirname(__file__), "agent3_payload.ini")

def _path(p: str) -> str:
    """Expand environment variables and normalize slashes."""
    return os.path.normpath(os.path.expandvars(p))

def run_agent3(patient_data: dict, vm_title: str = "WinXP for VB6",
               ahk_exe: str = None, agent3_ahk: str = None):
    """Builds the INI from calibration + patient_data, then runs agent3.ahk via AutoHotkey."""
    ahk_exe = _path(ahk_exe or os.getenv("AHK_EXE", AHK_EXE_DEFAULT))
    agent3_ahk = _path(agent3_ahk or os.getenv("AGENT3_AHK", AGENT3_AHK_DEFAULT))

    # --- sanity checks ---
    if not os.path.isfile(ahk_exe):
        raise FileNotFoundError(
            f"AutoHotkey.exe not found at:\n  {ahk_exe}\n"
            f"Install AHK v1 or set env var AHK_EXE to the correct path."
        )
    if not os.path.isfile(agent3_ahk):
        raise FileNotFoundError(
            f"agent3.ahk not found at:\n  {agent3_ahk}\n"
            f"Expected it next to this runner. If you placed it elsewhere, "
            f"set env var AGENT3_AHK or pass agent3_ahk=..."
        )
    if not os.path.isfile(CALIB_JSON):
        raise FileNotFoundError(
            f"calibration.json not found at:\n  {CALIB_JSON}\n"
            f"Run calibrate.py first and copy the file here."
        )

    # --- load calibration ---
    with open(CALIB_JSON, "r", encoding="utf-8") as f:
        coords = json.load(f)

    # helper to make "name_field=x,y" lines
    def pair(name: str) -> str:
        try:
            c = coords[name]
            return f"{name}={int(c['x'])},{int(c['y'])}"
        except Exception as e:
            raise KeyError(
                f"Missing/invalid coordinate for '{name}' in calibration.json. "
                f"Make sure keys exist and have x/y ints."
            ) from e

    # --- write INI payload for AHK ---
    ini_lines = [
        "[General]",
        f"window_title={vm_title}",
        "",
        "[Data]",
        f"name={patient_data.get('name','')}",
        f"address={patient_data.get('address','')}",
        f"date_of_birth={patient_data.get('date_of_birth','')}",
        f"age={patient_data.get('age','')}",
        f"sex={patient_data.get('sex','')}",
        "",
        "[Coords]",
        pair("name_field"),
        pair("address_field"),
        pair("date_of_birth_field"),
        pair("age_field"),
        pair("sex_field"),
        pair("add_button"),
        ""
    ]
    with open(PAYLOAD_INI, "w", encoding="utf-8") as f:
        f.write("\n".join(ini_lines))

    # --- call AutoHotkey ---
    cmd = [ahk_exe, agent3_ahk, PAYLOAD_INI]
    try:
        completed = subprocess.run(cmd, check=True)
        return completed.returncode
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Agent3 AHK failed (exit code {e.returncode}).\n"
            f"Command: {' '.join(cmd)}"
        ) from e

if __name__ == "__main__":
    # quick demo payload
    sample = {
        "name": "Jorge",
        "address": "10 Downing Street",
        "date_of_birth": "01/01/1980",
        "age": "45",
        "sex": "M"
    }
    try:
        run_agent3(sample)
        print("Agent3 completed.")
    except Exception as ex:
        print(f"[ERROR] {ex}", file=sys.stderr)
        sys.exit(1)
