# Legacy GUI Connector v2

A Python-based RPA (Robotic Process Automation) tool that bridges modern GUI applications with legacy systems running in virtual machines.

## Features

- **Modern Tkinter GUI**: Clean, user-friendly interface for patient data entry
- **VM Automation**: Automated form filling in legacy applications running in virtual machines
- **Smart Typing**: Uses pydirectinput for reliable keystroke injection into VMs
- **Calibration System**: Interactive coordinate mapping for different VM configurations
- **OCR Support**: Optional OCR table parsing for bulk data processing

## Components

### Core Files
- `main.py` - Application entry point
- `gui.py` - Modern Tkinter interface for data entry
- `automator.py` - RPA engine for VM automation
- `calibrate.py` - Interactive coordinate calibration tool

### Utilities
- `ocr_table_model.py` - OCR-based table parsing for bulk data processing
- `get_coords.py` - Simple coordinate capture utility
- `requirements.txt` - Python dependencies

## Installation

1. Clone the repository:
```bash
git clone https://github.com/R21Rash/legacy-gui-connector-v2.git
cd legacy-gui-connector-v2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install pydirectinput opencv-python
```

## Usage

### 1. Calibration
First, calibrate the coordinates for your VM:
```bash
python calibrate.py
```
Follow the prompts to hover over each field in your legacy application.

### 2. Running the Application
```bash
python main.py
```

### 3. OCR Processing (Optional)
For bulk data processing from images:
```bash
python ocr_table_model.py --learn <training_images_folder>
python ocr_table_model.py --parse <images_to_process_folder>
```

## Configuration

- Ensure your VM window title is exactly "WinXP for VB6"
- Keep the VM window visible and focused during automation
- The `calibration.json` file stores field coordinates (user-specific)

## Field Order
The automation fills fields in this sequence:
1. Name
2. Address  
3. Date of Birth
4. Age
5. Sex
6. Add Button

## Troubleshooting

- **Typing not working in VM**: Ensure pydirectinput is installed and VM has keyboard focus
- **Coordinates wrong**: Re-run calibration if VM window size/position changes
- **Uppercase letters**: The system uses Shift+key for reliable uppercase in VMs

## Dependencies

- pyautogui
- pygetwindow
- pyperclip
- pydirectinput
- opencv-python (for OCR)
- pytesseract (for OCR)
- numpy (for OCR)

## License

This project is open source. Please ensure compliance with your organization's policies when using RPA tools.
