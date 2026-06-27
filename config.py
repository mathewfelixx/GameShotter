import json
import os

CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "GameShotter")
CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.json")

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
}


def validate_config(cfg):
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
