"""Camera minigame logic and resources.

Provides:
- a VideoCapture wrapper (cap) used by the browser UI to show camera feed
- functions to handle successful brute force bypass behavior
"""
import cv2
from handlers import dialog_handler
from config import USERNAME_LIGHT, PASSWORD_LIGHT
from handlers.arduino_handler import send_command_to_arduino

# OpenCV camera setup used by camera minigame
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Warning: Camera not available for camera minigame.")

def on_bruteforce_success(state, exploit_name: str):
    """Handle state updates when brute force succeeds on the camera."""
    state.output_lines.append("[+]Brute force successful! The camera login has been bypassed!")
    state.output_lines.append(f"[+]The credentials are: Username: {USERNAME_LIGHT} | Password: {PASSWORD_LIGHT}")
    state.current_page["bypassed"] = True
    # switch to camera video page
    state.go_to_page_by_id("camera_video")
    send_command_to_arduino("C")
    
    dialog_handler.start_dialog(state, [
            "Nice!",
            "We used a brute-force attack to try a bunch of credentials against the camera and found some valid ones.",
            "Now we can see when they are at home...."
        ], char_delay=20)
    
    # Advance progression to indicate camera is hacked
    try:
        state.current_stage_index = max(state.current_stage_index, 1)
    except Exception:
        pass
