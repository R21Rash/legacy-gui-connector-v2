# calibrate.py (Final Version with corrected field name)
import pyautogui
import pygetwindow as gw
import json
import time

def calibrate_and_save():
    print("--- Starting Final UI Calibration ---")

    target_window_title = "WinXP for VB6" 
    try:
        vm_window = gw.getWindowsWithTitle(target_window_title)[0]
        vm_window.activate()
        print("SUCCESS: Found and activated the VM window.")
        time.sleep(1)
    except IndexError:
        print(f"ERROR: Could not find any window with title '{target_window_title}'.")
        return

    # --- UPDATED: Changed 'dob_field' to be more descriptive ---
    points_to_calibrate = {
        "name_field": "the Name input field",
        "address_field": "the Address input field",
        "date_of_birth_field": "the Date of Birth input field",
        "age_field": "the Age input field",
        "sex_field": "the Sex input field",
        "add_button": "the 'Add' button"
    }
    
    calibration_data = {}
    print("\n--- Auto-capture mode: You will have 5 seconds per target ---")
    for name, description in points_to_calibrate.items():
        print(f"\nHover your mouse over {description}. Capturing in:")
        for i in range(5, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        abs_pos = pyautogui.position()
        rel_x = abs_pos.x - vm_window.left
        rel_y = abs_pos.y - vm_window.top

        calibration_data[name] = {"x": rel_x, "y": rel_y}
        print(f"-> Captured '{name}' at relative coordinates: ({rel_x}, {rel_y})\n")

    with open("calibration.json", "w") as f:
        json.dump(calibration_data, f, indent=4)
        
    # --- Optional: capture context menu Paste offset relative to a right-click point ---
    print("\n--- Optional: Capture 'Paste' menu offset ---")
    print("This helps click the Paste entry without image matching.")
    print("Step 1: Hover your mouse over any text field inside the VM where the context menu opens.")
    print("        Capturing anchor point in:")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    anchor = pyautogui.position()
    anchor_rel_x = anchor.x - vm_window.left
    anchor_rel_y = anchor.y - vm_window.top
    print(f"-> Captured anchor at: ({anchor_rel_x}, {anchor_rel_y})")

    print("\nStep 2: Manually right-click at that field to open the context menu, then hover over the 'Paste' menu item.")
    print("        Capturing 'Paste' position in:")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    paste_pos = pyautogui.position()
    paste_rel_x = paste_pos.x - vm_window.left
    paste_rel_y = paste_pos.y - vm_window.top
    dx = paste_rel_x - anchor_rel_x
    dy = paste_rel_y - anchor_rel_y
    print(f"-> Captured 'Paste' offset dx,dy = ({dx}, {dy}) relative to the right-click point")

    # Save (append) the paste offset to the same calibration file
    try:
        with open("calibration.json", "r") as f:
            existing = json.load(f)
    except Exception:
        existing = {}
    existing.update(calibration_data)
    existing["paste_offset"] = {"dx": dx, "dy": dy}
    with open("calibration.json", "w") as f:
        json.dump(existing, f, indent=4)

    print("--- Calibration Complete! ---")
    print("Final coordinates and 'paste_offset' saved to 'calibration.json'.")

if __name__ == "__main__":
    calibrate_and_save()