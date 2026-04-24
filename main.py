import mss
import mss.tools
import os
from pynput import keyboard

save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "GameShots")

def take_screenshot():
    os.makedirs(save_dir, exist_ok=True)
    existing = [f for f in os.listdir(save_dir) if f.endswith(".png")]
    index = len(existing) + 1
    filepath = os.path.join(save_dir, f"shot-{index}.png")
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
    return filepath

def on_press(key):
    if key == keyboard.Key.f12:
        take_screenshot()

os.makedirs(save_dir, exist_ok=True)

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
