# get_coords.py
import pyautogui
import time

print("--- Mouse Coordinate Helper ---")
print("You have 5 seconds to move your mouse to the desired location.")
print("The script will then capture and print the coordinates.")

# Countdown from 5 to 1
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)

# Capture and print the coordinates after the delay
current_position = pyautogui.position()

print("\nSUCCESS! Captured Coordinates:")
print(current_position)