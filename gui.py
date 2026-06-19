import tkinter as tk
from tkinter import ttk, filedialog, messagebox

FKEYS = [f"f{i}" for i in range(1, 13)]

_window_open = False


def open_settings_window(cfg, on_save):
    global _window_open
    if _window_open:
        return
    _window_open = True

    root = tk.Tk()
    root.title("GameShotter Settings")
    root.resizable(False, False)

    pad = {"padx": 10, "pady": 6}

    save_dir_var = tk.StringVar(value=cfg["save_dir"])
    manual_var = tk.StringVar(value=cfg["hotkey_manual"])
    auto_var = tk.StringVar(value=cfg["hotkey_auto_toggle"])
    interval_var = tk.IntVar(value=cfg["auto_interval"])
    focus_hold_var = tk.IntVar(value=cfg["auto_focus_hold_seconds"])
    max_shots_var = tk.IntVar(value=cfg["auto_max_shots"])
    max_disk_var = tk.IntVar(value=cfg["auto_max_disk_mb"])
    format_var = tk.StringVar(value=cfg["image_format"])
    sound_var = tk.BooleanVar(value=cfg["sound_enabled"])
    startup_var = tk.BooleanVar(value=cfg["start_with_windows"])

    def browse_dir():
        chosen = filedialog.askdirectory(initialdir=save_dir_var.get())
        if chosen:
            save_dir_var.set(chosen)

    row = 0
    ttk.Label(root, text="Save folder:").grid(row=row, column=0, sticky="w", **pad)
    ttk.Entry(root, textvariable=save_dir_var, width=32).grid(row=row, column=1, **pad)
    ttk.Button(root, text="Browse", command=browse_dir).grid(row=row, column=2, **pad)

    row += 1
    ttk.Label(root, text="Manual screenshot key:").grid(row=row, column=0, sticky="w", **pad)
    ttk.Combobox(root, textvariable=manual_var, values=FKEYS, width=6, state="readonly").grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Label(root, text="Toggle auto-mode key:").grid(row=row, column=0, sticky="w", **pad)
    ttk.Combobox(root, textvariable=auto_var, values=FKEYS, width=6, state="readonly").grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Label(root, text="Auto-mode interval (seconds):").grid(row=row, column=0, sticky="w", **pad)
    ttk.Spinbox(root, from_=5, to=600, textvariable=interval_var, width=6).grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Label(root, text="Focus hold before auto-fire (seconds):").grid(row=row, column=0, sticky="w", **pad)
    ttk.Spinbox(root, from_=0, to=300, textvariable=focus_hold_var, width=6).grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Label(root, text="Max auto shots (0 = unlimited):").grid(row=row, column=0, sticky="w", **pad)
    ttk.Spinbox(root, from_=0, to=100000, textvariable=max_shots_var, width=6).grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Label(root, text="Max auto disk use MB (0 = unlimited):").grid(row=row, column=0, sticky="w", **pad)
    ttk.Spinbox(root, from_=0, to=1000000, textvariable=max_disk_var, width=6).grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Label(root, text="Image format:").grid(row=row, column=0, sticky="w", **pad)
    ttk.Combobox(root, textvariable=format_var, values=["png", "jpeg"], width=6, state="readonly").grid(row=row, column=1, sticky="w", **pad)

    row += 1
    ttk.Checkbutton(root, text="Play sounds", variable=sound_var).grid(row=row, column=0, columnspan=2, sticky="w", **pad)

    row += 1
    ttk.Checkbutton(root, text="Start with Windows", variable=startup_var).grid(row=row, column=0, columnspan=2, sticky="w", **pad)

    def save_and_close():
        if manual_var.get() == auto_var.get():
            messagebox.showerror("GameShotter", "Manual and auto-toggle keys must be different.")
            return
        new_cfg = {
            "save_dir": save_dir_var.get().strip() or cfg["save_dir"],
            "hotkey_manual": manual_var.get(),
            "hotkey_auto_toggle": auto_var.get(),
            "auto_interval": max(5, interval_var.get()),
            "auto_focus_hold_seconds": max(0, focus_hold_var.get()),
            "auto_max_shots": max(0, max_shots_var.get()),
            "auto_max_disk_mb": max(0, max_disk_var.get()),
            "image_format": format_var.get(),
            "sound_enabled": sound_var.get(),
            "start_with_windows": startup_var.get(),
        }
        on_save(new_cfg)
        close()

    def close():
        global _window_open
        _window_open = False
        root.destroy()

    row += 1
    btns = ttk.Frame(root)
    btns.grid(row=row, column=0, columnspan=3, pady=10)
    ttk.Button(btns, text="Save", command=save_and_close).pack(side="left", padx=5)
    ttk.Button(btns, text="Cancel", command=close).pack(side="left", padx=5)

    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()
