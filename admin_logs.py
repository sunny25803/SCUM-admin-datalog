import tkinter as tk
from tkinter import ttk
import re
from log_parser import read_file_with_fallback

def setup_admin_logs_gui(parent):
    columns = ("timestamp", "player_info", "command", "parameters")
    tree = ttk.Treeview(parent, columns=columns, show='headings')
    tree.heading("timestamp", text="时间")
    tree.heading("player_info", text="玩家信息")
    tree.heading("command", text="命令")
    tree.heading("parameters", text="参数")
    tree.pack(fill="both", expand=True)
    return tree

def parse_admin_log_file(log_file_path):
    pattern = re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): '(?P<player_id>\d{17}):(?P<player_name>.*?)\((?P<player_number>\d+)\)' Command: '(?P<command>\w+)\s*(?P<parameters>.*)'")

    log_lines = read_file_with_fallback(log_file_path)
    parsed_logs = []

    for line in log_lines:
        match = pattern.match(line.strip())
        if match:
            parsed_logs.append({
                'timestamp': match.group('timestamp'),
                'player_name': match.group('player_name'),
                'player_number': match.group('player_number'),
                'command': match.group('command'),
                'parameters': match.group('parameters'),
            })
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

def get_admin_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Player: {log['player_name']} ({log['player_number']}), "
                f"Command: {log['command']}, Parameters: {log['parameters']}"
            )
    return "\n".join(info_list)
