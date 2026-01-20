# AL-AI-Aim-Assistant
A real-time auto-aim proof-of-concept for Apex Legends that uses a custom YOLOv8 model to detect enemies and a spoofed Arduino HID device to assist aim.

## ⚠️ Important Notice
This project is for **educational and research purposes only**. Using automated aim assistance in online multiplayer games violates the Terms of Service of most games, including Apex Legends, and may result in permanent account bans. Use at your own risk.

## Features
- **Custom YOLOv8 Model**: Trained specifically to recognize Apex Legends character models
- **Dual Aim Modes**: 
  - **Magnet Aim**: Smooth tracking while holding ALT
  - **Silent Flick**: Rapid flick-and-return when pressing V
- **Hardware Integration**: Uses Arduino programmed as HID mouse for input simulation
- **Real-time Detection**: Captures and processes specific screen regions for minimal latency

## Prerequisites
- Python 3.8+
- NVIDIA GPU with CUDA support (for YOLOv8 acceleration)
- Arduino programmed as HID mouse with specific VID/PID
- Windows OS (due to `bettercam` and HID implementation)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/apex-ai-aim.git
cd apex-ai-aim

2. Install required packages:
```bash
pip install ultralytics bettercam keyboard colorama numpy

3. Install HID library for Arduino communication:
```bash
pip install hidapi

4. Place your trained YOLOv8 model (best_8s.pt) in the project root directory.

## Usage
1. Connect your Arduino HID mouse device
2. Run the main script with your device identifiers:
```bash
python apex-no-gui.py --vid 0x1234 --pid 0x5678 --pcode 0x01

## Controls
**ALT**: Enable magnet aim (smooth tracking)
**V**: Trigger silent flick (rapid flick shot)
**O**: Exit the program

## Project Structure
`apex-no-gui.py`: Main application with screen capture, detection, and aim logic
`mouse_instruct.py`: Low-level HID communication with Arduino mouse
`best_8s.pt`: Custom-trained YOLOv8 model (not included in repo)
`hidapi.dll`: Windows HID communication library

# How It Works
1. Captures a specific screen region (640x220 to 1280x860)
2. Processes frames through YOLOv8 to detect enemy hitboxes
3. Calculates distance from crosshair to nearest enemy center
4. Sends movement commands via HID to the Arduino mouse
5. Implements either smooth tracking or rapid flick based on keypress

## Limitations
1. Screen region coordinates are hardcoded for 1280x720 resolution
2. Requires specific Arduino HID firmware configuration
3. Model trained only on specific Apex Legends character skins
4. No prediction for enemy movement or bullet drop

