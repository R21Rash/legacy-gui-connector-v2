# paste_test.py
import pyperclip
import pyautogui
import time

text_to_paste = "This is a right-click paste test."

print("--- Starting Right-Click Paste Test ---")
print("You have 10 seconds to prepare...")
print("1. Go to your VM.")
print("2. Manually click your mouse inside the 'Name' input field.")
print("3. Wait for the script to continue...")

for i in range(10, 0, -1):
    print(f"{i}...", end="", flush=True)
    time.sleep(1)
print("\nAttempting to right-click and paste now!")

pyperclip.copy(text_to_paste)
time.sleep(0.5)

# --- NEW METHOD: Simulate a right-click and press 'p' ---
pyautogui.rightClick() # Right-clicks at the current mouse location
time.sleep(0.5)        # Wait for the context menu to appear
pyautogui.press('p')   # Press the 'p' key to select "Paste"
# ----------------------------------------------------

print("\n--- Test Complete ---")
print("Check the 'Name' field. Did the right-click method work?")