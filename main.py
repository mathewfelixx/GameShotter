import mss
import mss.tools
import os
import sys
import ctypes
import psutil
import threading
import time
from pynput import keyboard
from playsound import playsound
import pystray
from pystray import MenuItem as item
from PIL import Image

import config

settings = config.load_config()

auto_mode = False
auto_timer = None
current_keys = set()

auto_target_window = None
focus_window = None
focus_since = 0.0
focus_thread = None

auto_shot_count = 0
auto_bytes_written = 0

def get_icon_path():
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Gameshotter.ico")

def play_sound(filename):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, filename)
    threading.Thread(target=lambda: playsound(path), daemon=True).start()

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

def take_screenshot(auto=False, window_title=None):
    title = sanitise(window_title or get_active_window_title())
    app_folder = os.path.join(settings["save_dir"], title)
    os.makedirs(app_folder, exist_ok=True)

    if auto:
        subfolder = os.path.join(app_folder, "auto")
    else:
        subfolder = app_folder

    os.makedirs(subfolder, exist_ok=True)

    index = get_next_index_in(subfolder, title, "png")
    filepath = os.path.join(subfolder, f"{title}-{index}.png")

    with mss.mss() as sct:
        monitor = sct.monitors[0]
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        if not auto:
            play_sound("gameshotter manual.wav")

    return filepath

def focus_tracker():
    global focus_window, focus_since
    last_title = None
    while auto_mode:
        title = get_active_window_title()
        if title != last_title:
            last_title = title
            focus_window = title
            focus_since = time.time()
        time.sleep(1)

def auto_loop():
    global auto_timer, auto_shot_count, auto_bytes_written
    if not auto_mode:
        return

    hold_needed = settings["auto_focus_hold_seconds"]
    if focus_window == auto_target_window and (time.time() - focus_since) >= hold_needed:
        filepath = take_screenshot(auto=True, window_title=auto_target_window)
        auto_shot_count += 1
        auto_bytes_written += os.path.getsize(filepath)

        max_shots = settings["auto_max_shots"]
        max_disk_mb = settings["auto_max_disk_mb"]
        hit_shot_cap = max_shots and auto_shot_count >= max_shots
        hit_disk_cap = max_disk_mb and auto_bytes_written >= max_disk_mb * 1024 * 1024
        if hit_shot_cap or hit_disk_cap:
            toggle_auto()
            return

    auto_timer = threading.Timer(settings["auto_interval"], auto_loop)
    auto_timer.start()

def toggle_auto():
    global auto_mode, auto_timer, auto_target_window, focus_thread
    global auto_shot_count, auto_bytes_written
    auto_mode = not auto_mode
    if auto_mode:
        auto_target_window = get_active_window_title()
        auto_shot_count = 0
        auto_bytes_written = 0
        play_sound("gameshotter auto mode start.wav")
        focus_thread = threading.Thread(target=focus_tracker, daemon=True)
        focus_thread.start()
        auto_loop()
    else:
        if auto_timer:
            auto_timer.cancel()
            auto_timer = None
        auto_target_window = None
        play_sound("gameshotter auto mode stop.wav")

def exit_app(icon, item):
    icon.stop()
    os._exit(0)

def key_name(key):
    if isinstance(key, keyboard.KeyCode):
        return None
    return key.name

def on_press(key):
    current_keys.add(key)
    pressed = key_name(key)
    ctrl_held = keyboard.Key.ctrl_l in current_keys or keyboard.Key.ctrl_r in current_keys

    if ctrl_held and pressed == "f12":
        exit_app(tray_icon, None)
    elif pressed == settings["hotkey_manual"]:
        take_screenshot(auto=False)
    elif pressed == settings["hotkey_auto_toggle"]:
        toggle_auto()

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

os.makedirs(settings["save_dir"], exist_ok=True)
play_sound("gameshotter intro.wav")

tray_thread = threading.Thread(target=start_tray, daemon=True)
tray_thread.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
