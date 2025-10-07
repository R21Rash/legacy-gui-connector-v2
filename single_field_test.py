# single_field_test.py (Final Version with Image Recognition)
import pyautogui
import pygetwindow as gw
import json
import time
import pyperclip 

def test_name_field_with_image():
    """
    Tests the final method: right-click, then find and click the 'Paste' image.
    """
    # Make sure you have the required library
    try:
        import cv2
    except ImportError:
        print("ERROR: The 'opencv-python' library is not installed.")
        print("Please run: py -m pip install opencv-python")
        return
        
    try:
        with open("calibration.json", "r") as f:
            coords = json.load(f)
    except FileNotFoundError:
        print("ERROR: calibration.json not found. Please run calibrate.py for the 'name_field'.")
        return

    target_window_title = "WinXP for VB6"
    try:
        vm_window = gw.getWindowsWithTitle(target_window_title)[0]
        vm_window.activate()
        time.sleep(1) 
        pyautogui.click(vm_window.left + 100, vm_window.top + 15)
        time.sleep(0.5)

    except IndexError:
        print(f"ERROR: The '{target_window_title}' window was not found.")
        return
    
    value_to_paste = "Fahmy"
    print(f"Attempting to paste '{value_to_paste}' into the Name field...")
    
    field_coords = coords["name_field"]
    click_x = vm_window.left + field_coords['x']
    click_y = vm_window.top + field_coords['y']
    
    pyautogui.click(click_x, click_y)
    time.sleep(0.5)
    
    pyperclip.copy(value_to_paste)
    time.sleep(0.2)
    
    pyautogui.rightClick(click_x, click_y)
    time.sleep(1) # Give the menu a full second to appear
    
    # --- THE FINAL STEP: FIND AND CLICK THE IMAGE ---
    try:
        print("Looking for 'paste_button.png' on the screen...")
        # Use the screenshot you made to find the button
        paste_location = pyautogui.locateCenterOnScreen('paste_button.png', confidence=0.8)

        if paste_location is None:
            print("ERROR: Could not find the 'paste_button.png' image on the screen.")
            return

        # Click on the location of the found image
        pyautogui.click(paste_location)
        print("SUCCESS! Clicked 'Paste' using image recognition!")

    except Exception as e:
        print(f"An error occurred during image recognition: {e}")
        print("Make sure 'paste_button.png' is saved in the correct folder.")

    print("\n--- Test Complete! Check the VM. ---")

if __name__ == "__main__":
    test_name_field_with_image()