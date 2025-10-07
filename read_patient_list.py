# read_patient_list.py (Ultimate Self-Contained Version)
import pyautogui
import pytesseract
from PIL import Image
import json
import cv2
import numpy as np
import time
import re

# This path should point to your Tesseract installation.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Your captured coordinates
TOP_LEFT_CORNER = (256, 367)
BOTTOM_RIGHT_CORNER = (1862, 753)

def advanced_parse_ocr_data(text):
    """Uses Regular Expressions (regex) to intelligently parse the OCR text."""
    patients = []
    lines = text.strip().split('\n')
    date_pattern = re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}')
    
    # Skip header line by starting the loop from the second line
    for line in lines[1:]:
        if not line.strip(): continue
        
        # Find the date to anchor our parsing
        match = date_pattern.search(line)
        if not match: continue

        try:
            date_of_birth = match.group(0)
            before_date = line[:match.start()].strip()
            after_date = line[match.end():].strip()

            before_parts = before_date.split()
            patient_id = before_parts[0]
            patient_name = before_parts[1]
            address = " ".join(before_parts[2:])
            age_sex = after_date.strip()

            if patient_id.isdigit():
                patients.append({
                    "Patient_ID": patient_id, "Patient_Name": patient_name,
                    "Address": address, "Date_Of_Birth": date_of_birth,
                    "Age/Sex": age_sex
                })
        except (IndexError, AttributeError):
            continue
            
    return patients

def read_patient_data():
    """Applies a definitive, simplified pipeline for maximum OCR accuracy."""
    
    left, top = TOP_LEFT_CORNER
    width = BOTTOM_RIGHT_CORNER[0] - left
    height = BOTTOM_RIGHT_CORNER[1] - top
    
    if width <= 0 or height <= 0:
        print("ERROR: The corner coordinates are incorrect.")
        return

    print(f"Capturing screen region: Left={left}, Top={top}, Width={width}, Height={height}")
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    
    # --- ULTIMATE IMAGE PROCESSING PIPELINE ---
    
    # 1. Convert to OpenCV format and upscale (the most effective step)
    img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    img_cv = cv2.resize(img_cv, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 2. Apply an inverted binary threshold to get clean black text on a white background
    # This is a simple and powerful way to create a high-contrast image.
    _, img_cv = cv2.threshold(img_cv, 128, 255, cv2.THRESH_BINARY_INV)
    # --- END OF PROCESSING ---

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    final_image_path = f"debug_ultimate_{timestamp}.png"
    cv2.imwrite(final_image_path, img_cv)
    print(f"Saved final processed image to: {final_image_path}")
    
    print("\n--- Reading Data from Screen ---")
    # Use Page Segmentation Mode 6, which is optimized for tables
    config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(img_cv, config=config)
    
    print("\n--- Raw OCR Text Output ---")
    print(extracted_text)
    
    patient_list = advanced_parse_ocr_data(extracted_text)
    
    print("\n--- Parsed Patient Data (Final) ---")
    print(json.dumps(patient_list, indent=4))

if __name__ == "__main__":
    read_patient_data()