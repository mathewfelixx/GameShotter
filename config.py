import json
import os
import sys
import winreg

CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "GameShotter")
CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.json")

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "GameShotter"

FKEYS = [f"f{i}" for i in range(1, 13)]

DEFAULTS = {
    "save_dir": os.path.join(os.path.expanduser("~"), "Pictures", "GameShots"),
    "hotkey_manual": "f12",
    "hotkey_auto_toggle": "f6",
    "auto_interval": 30,
    "auto_focus_hold_seconds": 3,
    "auto_max_shots": 0,
    "auto_max_disk_mb": 0,
    "image_format": "png",
    "sound_enabled": True,
    "start_with_windows": False,
}


def validate_config(cfg):
    # checks each saved setting is sane, falls back to the default if not
    valid = DEFAULTS.copy()

    if isinstance(cfg.get("save_dir"), str) and cfg["save_dir"].strip():
        valid["save_dir"] = cfg["save_dir"]

    if cfg.get("hotkey_manual") in FKEYS:
        valid["hotkey_manual"] = cfg["hotkey_manual"]

    if cfg.get("hotkey_auto_toggle") in FKEYS:
        valid["hotkey_auto_toggle"] = cfg["hotkey_auto_toggle"]

    if isinstance(cfg.get("auto_interval"), (int, float)) and 5 <= cfg["auto_interval"] <= 600:
        valid["auto_interval"] = int(cfg["auto_interval"])

    if isinstance(cfg.get("auto_focus_hold_seconds"), (int, float)) and 0 <= cfg["auto_focus_hold_seconds"] <= 300:
        valid["auto_focus_hold_seconds"] = int(cfg["auto_focus_hold_seconds"])

    if isinstance(cfg.get("auto_max_shots"), int) and 0 <= cfg["auto_max_shots"] <= 100000:
        valid["auto_max_shots"] = cfg["auto_max_shots"]

    if isinstance(cfg.get("auto_max_disk_mb"), (int, float)) and 0 <= cfg["auto_max_disk_mb"] <= 1000000:
        valid["auto_max_disk_mb"] = cfg["auto_max_disk_mb"]

    if cfg.get("image_format") in ("png", "jpeg"):
        valid["image_format"] = cfg["image_format"]

    if isinstance(cfg.get("sound_enabled"), bool):
        valid["sound_enabled"] = cfg["sound_enabled"]

    if isinstance(cfg.get("start_with_windows"), bool):
        valid["start_with_windows"] = cfg["start_with_windows"]

    return valid


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                saved = json.load(f)
            return validate_config(saved)
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULTS.copy()


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def set_start_with_windows(enabled):
    launch_target = sys.executable if getattr(sys, "frozen", False) else \
        f'"{sys.executable}" "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")}"'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, RUN_NAME, 0, winreg.REG_SZ, launch_target)
        else:
            try:
                winreg.DeleteValue(key, RUN_NAME)
            except FileNotFoundError:
                pass
