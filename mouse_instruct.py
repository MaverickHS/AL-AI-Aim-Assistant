import ctypes
import os

# Load the DLL explicitly
dll_path = r"C:\Users\dhkni\OneDrive\Documents\Arduino\Apex\ApexAI\hidapi.dll"
try:
    ctypes.CDLL(dll_path)
except Exception as e:
    print(f"Failed to load DLL: {e}")

# Now try to import your library
import hid

import hid  # For USB HID communication
import time  # For timing operations

MOUSE_LEFT = 0x01  # Left mouse button mask
MOUSE_RIGHT = 0x02  # Right mouse button mask
MOUSE_MIDDLE = 0x04  # Middle mouse button mask
MOUSE_ALL = MOUSE_LEFT | MOUSE_RIGHT | MOUSE_MIDDLE  # All buttons mask


class DeviceNotFoundError(Exception):
    # Custom exception for device not found
    pass


class MouseInstruct:
    def __init__(self, device):
        self._buttons_mask = 0x0  # Current button state
        self._device = device  # HID device handle
        self.move(0, 0)  # Initialize mouse position

    @classmethod
    def get_mouse(cls, vid=None, pid=None, ping_code=None):
        # Find and connect to the Arduino HID mouse
        device = find_mouse_device(vid, pid, ping_code)
        if not device:
            vid_str = hex(vid) if vid else "Unspecified"
            pid_str = hex(pid) if pid else "Unspecified"
            ping_code_str = hex(ping_code) if pid else "Unspecified"
            error_msg = f"[-] Device VID: {vid_str} PID: {pid_str} Ping code: {ping_code_str} not found!"
            raise DeviceNotFoundError(error_msg)
        return cls(device)

    def _buttons(self, buttons):
        # Update button mask and send report if changed
        if buttons != self._buttons_mask:
            self._buttons_mask = buttons
            self.move(0, 0)

    def _make_report(self, x, y):
        # Create HID report for mouse movement and button state
        report_data = [
            0x01, # Report ID: 0
            self._buttons_mask,
            x & 0xFF, (x >> 8) & 0xFF,
            y & 0xFF, (y >> 8) & 0xFF
        ]
        return report_data

    def _send_raw_report(self, report_data):
        # Send raw HID report to device
        self._device.write(report_data)

    def click(self, button=MOUSE_LEFT):
        # Simulate mouse click
        self._buttons_mask = button
        self.move(0, 0)
        self._buttons_mask = 0
        self.move(0, 0)

    def silent_flick(self, x, y, button=MOUSE_LEFT):
        # Move mouse quickly and return to original position (silent flick)
        self._buttons_mask = button
        self.move(x, y)
        time.sleep(0.006)
        self._buttons_mask = 0
        self.move(-x, -y)

    def press(self, button=MOUSE_LEFT):
        # Press mouse button
        self._buttons(self._buttons_mask | button)

    def release(self, button = MOUSE_LEFT):
        # Release mouse button
        self._buttons(self._buttons_mask & ~button)

    def is_pressed(self, button = MOUSE_LEFT):
        # Check if button is pressed
        return bool(button & self._buttons_mask)

    def move(self, x, y):
        # Move mouse by sending HID report
        self._send_raw_report(self._make_report(limit_xy(x), limit_xy(y)))


def check_ping(dev, ping_code):
    # Check if device responds to ping code
    dev.write(bytes([0, ping_code]))
    try:
        resp = dev.read(max_length = 1, timeout_ms = 10)
    except OSError as e:
        return False
    else:
        return resp and resp[0] == ping_code

def find_mouse_device(vid, pid, ping_code):
    # Search for HID device matching VID, PID, and ping code
    # device = hid.Device()
    for dev_info in hid.enumerate(vid, pid):
        device = hid.Device(path=dev_info['path'])
        found = check_ping(device, ping_code)
        if found:
            return device
        else:
            device.close()
    return None

def low_byte(x):
    # Get low byte of integer
    return x & 0xFF

def high_byte(x):
    # Get high byte of integer
    return (x >> 8) & 0xFF

def limit_xy(xy):
    # Limit mouse movement to HID range
    if xy < -32767:
        return -32767
    elif xy > 32767:
        return 32767
    else: return xy