import time  # For timing operations
import numpy as np  # For numerical calculations
import keyboard  # For keyboard input detection
import argparse  # For parsing command line arguments
import bettercam  # For camera capture

from colorama import Fore  # For colored terminal output
from ultralytics import YOLO  # For YOLO object detection model
from mouse_instruct import MouseInstruct  # For Arduino HID mouse control

SMOOTH_X = 0.8  # Smoothing factor for X axis movement
SMOOTH_Y = 0.8  # Smoothing factor for Y axis movement

class Apex:
    def __init__(self, VID, PID, PING_CODE):
        # Initialize camera with RGB output
        self.cam = bettercam.create(output_color="RGB")
        # Initialize mouse HID using Arduino
        self.mouse = MouseInstruct.get_mouse(VID, PID, PING_CODE)
        # Load YOLO model for enemy detection, use GPU
        self.model = YOLO('./best_8s.pt').to('cuda')

    def get_xy(self):
        # Capture a region of the screen
        frame = self.cam.grab(region=(640, 220, 1280, 860))
        dx, dy = None, None  # Default movement deltas
        if frame is None:
            return dx, dy  # Return if no frame captured

        # Run YOLO detection on the frame
        results = self.model.predict(frame, verbose=False, conf=0.45)
        if results and len(results) > 0:
            # Get bounding boxes of detected enemies
            enemy_boxes = results[0].boxes.xyxy.cpu().numpy()
            min_dist = float('inf')  # Track closest enemy

            center_x, center_y = 320, 320  # Center of aim region

            # Find the closest enemy to the center
            for box in enemy_boxes:
                x1, y1, x2, y2 = box

                enemy_center_x = (x1 + x2) / 2
                enemy_center_y = (y1 + y2) / 2

                tx = enemy_center_x - center_x
                ty = enemy_center_y - center_y

                distance = np.hypot(tx, ty)  # Euclidean distance

                if distance < min_dist:
                    min_dist = distance
                    dx, dy = tx, ty - 10  # Aim slightly below center

        return dx, dy  # Return movement deltas

    def update(self):
        # Main loop for auto-aim control
        while True:
            # Exit if 'o' is pressed
            if keyboard.is_pressed('o'):
                self.cam.stop()
                exit(0)

            # Magnet aim if 'alt' is pressed
            if keyboard.is_pressed('alt'):
                dx, dy = self.get_xy()
                if dx is not None and dy is not None:
                    # Move mouse smoothly towards enemy
                    start = time.perf_counter()
                    self.mouse.move(int(dx * SMOOTH_X), int(dy * SMOOTH_Y))
                    print(f"Magnet {(time.perf_counter() - start):.4f}")

            # Silent flick aim if 'v' is pressed
            if keyboard.is_pressed('v'):
                dx, dy = self.get_xy()
                if dx is not None and dy is not None:
                    start = time.perf_counter()
                    self.mouse.silent_flick(int(dx * 1.4), int(dy * 1.4))
                    print(f"Silent flick {(time.perf_counter() - start):.4f}")
            else:
                time.sleep(0.01)  # Sleep briefly to reduce CPU usage

if __name__ == '__main__':
    # Parse command line arguments for mouse HID
    parser = argparse.ArgumentParser()
    parser.add_argument('--vid', help='Vendor ID of your mouse', default=None)
    parser.add_argument('--pid', help='Product ID of your mouse', default=None)
    parser.add_argument('--pcode', help='Pingcode of your mouse', default=None)

    args = parser.parse_args()

    # Initialize YOLO and mouse HID
    print(f'{Fore.LIGHTWHITE_EX}Initializing YOLO...', end='')
    apex = Apex(int(args.vid, 16), int(args.pid, 16), int(args.pcode, 16))
    print(f'\r{Fore.LIGHTWHITE_EX}Initialized         ', end='\n', flush=True)
    print(f'{Fore.LIGHTWHITE_EX}"Alt" - Magnet')
    print(f'{Fore.LIGHTWHITE_EX} "V"  - Silent')
    print(f'{Fore.LIGHTWHITE_EX} "O"  - Exit  ')
    apex.update()  # Start auto-aim loop
