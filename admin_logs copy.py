import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
from log_parser import parse_log_file

def setup_admin_logs_gui(root):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    log_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    log_display.pack(fill="both", expand=True)

    def load_all_admin_logs():
        log_files = [f for f in os.listdir() if f.startswith('admin_') and f.endswith('.log')]
        log_entries = []
        for log_file in log_files:
            log_entries.extend(parse_log_file(log_file))
        log_entries.sort()
        log_display.delete(1.0, tk.END)
        for entry in log_entries:
            timestamp, player_info, event_type, event_info = entry
            log_display.insert(tk.END, f"{timestamp}: {player_info} {event_type}: {event_info}\n")

    open_button = tk.Button(frame, text="Load All Admin Logs", command=load_all_admin_logs)
    open_button.pack(side=tk.TOP, fill="x")

    return frame
