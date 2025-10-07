# automator.py - FINAL PROJECT VERSION (with clipboard fix)
import pyautogui
import pygetwindow as gw
import json
import time
import pyperclip 
try:
    import pydirectinput as pdi
except Exception:
    pdi = None

def fill_patient_form(patient_data):
    """
    Automates filling the entire patient form with a robust clipboard method.
    """
    try:
        with open("calibration.json", "r") as f:
            coords = json.load(f)
    except FileNotFoundError:
        raise Exception("Calibration file 'calibration.json' not found. Please run 'calibrate.py' first.")

    target_window_title = "WinXP for VB6"
    try:
        vm_window = gw.getWindowsWithTitle(target_window_title)[0]
        vm_window.activate()
        time.sleep(1) 
        
        print("Forcefully focusing the VM window by clicking its title bar...")
        pyautogui.click(vm_window.left + 100, vm_window.top + 15)
        time.sleep(0.5)
        # Extra: click inside client area to ensure keyboard capture by the VM
        try:
            center_x = vm_window.left + vm_window.width // 2
            center_y = vm_window.top + vm_window.height // 2
            pyautogui.click(center_x, center_y)
            time.sleep(0.3)
        except Exception:
            pass

    except IndexError:
        raise Exception(f"The '{target_window_title}' window was not found. Is the application running in the VM?")
    
    # Helper: key press using pydirectinput if available, else pyautogui
    def press_key(key: str, delay: float = 0.05):
        if pdi:
            pdi.press(key)
        else:
            pyautogui.press(key)
        time.sleep(delay)

    def key_down(key: str):
        if pdi:
            pdi.keyDown(key)
        else:
            pyautogui.keyDown(key)
        time.sleep(0.02)

    def key_up(key: str):
        if pdi:
            pdi.keyUp(key)
        else:
            pyautogui.keyUp(key)
        time.sleep(0.02)

    def type_text(text: str, interval: float = 0.05):
        if not text:
            return
        if pdi:
            # pydirectinput.write ignores interval per char; emulate
            for ch in str(text):
                if ch.isalpha() and ch.isupper():
                    # Hold Shift to produce uppercase reliably in VMs
                    pdi.keyDown('shift')
                    pdi.press(ch.lower())
                    pdi.keyUp('shift')
                else:
                    pdi.press(ch)
                time.sleep(interval)
        else:
            pyautogui.typewrite(str(text), interval=interval)

    # --- UPDATED: Click each field explicitly before typing (more reliable than Tab in VMs) ---
    field_order = ["name_field", "address_field", "date_of_birth_field", "age_field", "sex_field"]

    for i, field_name in enumerate(field_order):
        data_key = field_name.replace("_field", "")
        value_to_type = patient_data.get(data_key, "")
        print(f"Typing '{value_to_type}' into {data_key} field...")

        # Focus the exact field via calibrated coordinates
        field_coords = coords[field_name]
        click_x = vm_window.left + field_coords['x']
        click_y = vm_window.top + field_coords['y']
        pyautogui.click(click_x, click_y)
        time.sleep(0.2)

        # Clear any existing text and type the new value
        key_down('ctrl'); press_key('a', delay=0.02); key_up('ctrl')
        press_key('backspace', delay=0.05)
        time.sleep(0.05)
        # Special handling for sex field: normalize to first letter and uppercase
        if data_key == "sex":
            normalized = str(value_to_type).strip().upper()[:1]
            if normalized not in ("M", "F") and normalized:
                # Try first alpha char
                for ch in str(value_to_type):
                    if ch.isalpha():
                        normalized = ch.upper()
                        break
            if normalized in ("M", "F"):
                type_text(normalized, interval=0.07)
                time.sleep(0.1)
            else:
                # Fallback for dropdowns: open menu and select by first letter
                press_key('alt', delay=0.05)  # noop if not used by control
                press_key('down', delay=0.1)
                if value_to_type:
                    type_text(str(value_to_type)[0].upper(), interval=0.07)
                press_key('enter', delay=0.1)
        else:
            type_text(str(value_to_type), interval=0.07)
        time.sleep(0.1)

        
    add_button_coords = coords["add_button"]
    print("Clicking the 'Add' button...")
    pyautogui.click(vm_window.left + add_button_coords['x'], vm_window.top + add_button_coords['y'])
    
    print("Automation completed successfully!")