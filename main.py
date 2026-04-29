import mss
import mss.tools
import os
import sys
import ctypes
import psutil
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

def get_active_window_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        exe = psutil.Process(pid.value).name()
        return os.path.splitext(exe)[0]
    except:
        return "Unknown"

def sanitise(name):
    return "".join(c for c in name if c.isalnum() or c in " -_").strip().replace(" ", "-")

def get_next_index_in(subfolder, window_name, ext):
    prefix = f"{window_name}-"
    existing = [f for f in os.listdir(subfolder) if f.startswith(prefix) and f.endswith(f".{ext}")]
    return len(existing) + 1

def take_screenshot():
    title = sanitise(get_active_window_title())
    app_folder = os.path.join(save_dir, title)
    os.makedirs(app_folder, exist_ok=True)
    index = get_next_index_in(app_folder, title, "png")
    filepath = os.path.join(app_folder, f"{title}-{index}.png")
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
