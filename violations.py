import re
import tkinter as tk
from tkinter import ttk
from log_parser import read_file_with_fallback, parse_violation_log_file  # 从 log_parser 导入

def setup_violations_gui(parent):
    columns = ("timestamp", "player_name", "player_id", "violation", "details")
    tree = ttk.Treeview(parent, columns=columns, show='headings')
    tree.heading("timestamp", text="时间")
    tree.heading("player_name", text="玩家姓名")
    tree.heading("player_id", text="玩家ID")
    tree.heading("violation", text="违规行为")
    tree.heading("details", text="详情")
    tree.pack(fill="both", expand=True)
    return tree

def get_violation_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Player: {log.get('player_name', 'N/A')} ({log.get('player_id', 'N/A')}), "
                f"Violation: {log['violation']}, Details: {log['details']}"
            )
    return "\n".join(info_list)

def read_file_with_fallback(file_path):
    encodings = [None, 'utf-8', 'gbk', 'utf-16', 'utf-16le', 'utf-16be']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as file:
                return file.readlines()
        except (UnicodeDecodeError, TypeError, UnicodeError):
            continue

    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            try:
                return raw_data.decode('utf-16').splitlines()
            except UnicodeDecodeError:
                return raw_data.decode('utf-16le').splitlines()
    except UnicodeDecodeError:
        raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Failed to decode {file_path} with encodings {encodings}")
