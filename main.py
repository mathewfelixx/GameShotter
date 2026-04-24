import mss
import mss.tools
import os
import sys
import threading
from pynput import keyboard
import pystray
from pystray import MenuItem as item
from PIL import Image

save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "GameShots")

current_keys = set()

def get_icon_path():
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Gameshotter.ico")

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

def exit_app(icon, item):
    icon.stop()
    os._exit(0)

def on_press(key):
    current_keys.add(key)
    ctrl_held = keyboard.Key.ctrl_l in current_keys or keyboard.Key.ctrl_r in current_keys
    if ctrl_held and key == keyboard.Key.f12:
        exit_app(tray_icon, None)
    elif key == keyboard.Key.f12:
        take_screenshot()

def on_release(key):
    current_keys.discard(key)

def start_tray():
    global tray_icon
    image = Image.open(get_icon_path())
    menu = pystray.Menu(
        item("GameShotter V1", lambda: None, enabled=False),
        item("Exit", exit_app)
    )
    tray_icon = pystray.Icon("GameShotter", image, "GameShotter", menu)
    tray_icon.run()

os.makedirs(save_dir, exist_ok=True)

tray_thread = threading.Thread(target=start_tray, daemon=True)
tray_thread.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
