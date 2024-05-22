import tkinter as tk
from tkinter import ttk
import re
from log_parser import read_file_with_fallback

def setup_login_logs_gui(parent):
    columns = ("timestamp", "ip", "steam_id", "player_name", "player_number", "action", "location")
    tree = ttk.Treeview(parent, columns=columns, show='headings')
    tree.heading("timestamp", text="时间")
    tree.heading("ip", text="IP地址")
    tree.heading("steam_id", text="Steam ID")
    tree.heading("player_name", text="玩家名称")
    tree.heading("player_number", text="玩家编号")
    tree.heading("action", text="操作")
    tree.heading("location", text="位置")
    tree.pack(fill="both", expand=True)
    return tree

def parse_login_log_file(log_file_path):
    pattern = re.compile(
        r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): '(?P<ip>[\d\.]+) (?P<steam_id>\d+):(?P<player_name>.*?)\((?P<player_number>\d+)\)' (?P<action>logged in|logged out) at: (?P<location>.*)"
    )

    log_lines = read_file_with_fallback(log_file_path)
    parsed_logs = []

    for line in log_lines:
        match = pattern.match(line.strip())
        if match:
            parsed_logs.append({
                'timestamp': match.group('timestamp'),
                'ip': match.group('ip'),
                'steam_id': match.group('steam_id'),
                'player_name': match.group('player_name'),
                'player_number': match.group('player_number'),
                'action': match.group('action'),
                'location': match.group('location'),
            })
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

def get_login_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, IP: {log['ip']}, Steam ID: {log['steam_id']}, "
                f"Player: {log['player_name']} {log['player_number']}, Action: {log['action']}, "
                f"Location: {log['location']}"
            )
    return "\n".join(info_list)
