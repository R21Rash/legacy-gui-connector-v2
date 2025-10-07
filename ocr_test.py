# ocr_test.py
import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image
import time
import pyperclip

# --- IMPORTANT ---
# You must tell pytesseract where you installed the Tesseract application.
# Update this path to your Tesseract installation location.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_text_and_paste():
    """Finds a window, takes a screenshot, and uses OCR to find and interact with a field."""
    
    # The text label we want to find on the screen
    label_to_find = "Name" # This is case-sensitive

    target_window_title = "WinXP for VB6"
    try:
        vm_window = gw.getWindowsWithTitle(target_window_title)[0]
        vm_window.activate()
        time.sleep(1)
        print(f"SUCCESS: Found and activated the '{target_window_title}' window.")
    except IndexError:
        print(f"ERROR: Could not find window '{target_window_title}'. Is the VM running?")
        return

    # Take a screenshot of just the VM window for OCR processing
    screenshot = pyautogui.screenshot(region=(
        vm_window.left, vm_window.top, vm_window.width, vm_window.height
    ))
    
    # Use pytesseract to get detailed data about all text in the image
    # This gives us the text of each word and its x, y, width, and height
    data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
    
    print("\n--- OCR Results ---")
    
    # Loop through all the words found by OCR to find our label
    num_boxes = len(data['level'])
    found = False
    for i in range(num_boxes):
        # Check if the found text exactly matches our label
        if label_to_find == data['text'][i]:
            found = True
            # Get the coordinates of the found label
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            
            print(f"Found the label '{data['text'][i]}' at relative position (x={x}, y={y})")
            
            # Estimate the center of the input field to the right of the label
            # We move right by the width of the label, add a guess for the gap, and center vertically
            input_field_x = x + w + 70 # Adjust the '70' if the click is off
            input_field_y = y + (h // 2)

            print(f"Estimating input field center is at ({input_field_x}, {input_field_y})")
            
            # Convert the relative coordinates back to absolute screen coordinates for the click
            abs_click_x = vm_window.left + input_field_x
            abs_click_y = vm_window.top + input_field_y
            
            # Click and paste into the estimated location
            pyautogui.click(abs_click_x, abs_click_y)
            pyperclip.copy("OCR Test Successful!")
            pyautogui.hotkey('ctrl', 'v') # Using Ctrl+V as it works on most standard inputs
            
            print("\n--- Automation Complete! ---")
            break # Stop searching once we've found and used the label
            
    if not found:
        print(f"Could not find the text label '{label_to_find}' on the screen.")

if __name__ == "__main__":
    find_text_and_paste()