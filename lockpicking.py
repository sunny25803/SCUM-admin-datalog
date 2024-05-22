import re
import tkinter as tk
from tkinter import ttk
from log_parser import read_file_with_fallback
from zone_determiner import determine_zone  # 导入区块计算函数

# 锁类型翻译字典
lock_type_translation = {
    "Basic": "基础",
    "Advanced": "高级",
    "DialLock": "拨号锁",
    "Medium": "中级"
}

def setup_logs_gui(parent, columns, title):
    window = tk.Toplevel(parent)
    window.title(title)
    tree = ttk.Treeview(window, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
    
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    
    return tree

def parse_log_file(log_file_path):
    lockpicking_patterns = [
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[LogMinigame\] \[.*?\] User: (?P<player_name>.*?) \(\d+, (?P<steam_id>\d{17})\)\. "
            r"Success: (?P<success>Yes|No)\. Elapsed time: (?P<elapsed_time>[\d\.]+)\. Failed attempts: (?P<failed_attempts>\d+)\. "
            r"Target object: (?P<target_object>.*?)\(ID: (?P<target_object_id>.*?)\)\. Lock type: (?P<lock_type>.*?)\. "
            r"User owner: \d+\(\[(?P<user_owner_steam_id>\d{17})\] (?P<user_owner_name>.*?)\)\. Location: (?P<location>.*?)$"
        ),
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[LogMinigame\] \[.*?\] User: (?P<player_name>.*?) \(\d+, (?P<steam_id>\d{17})\)\. "
            r"Success: (?P<success>Yes|No)\. Elapsed time: (?P<elapsed_time>[\d\.]+)\. Failed attempts: (?P<failed_attempts>\d+)\. "
            r"Target object: (?P<target_object>.*?)\(ID: N/A\)\. Lock type: (?P<lock_type>.*?)\. User owner: N/A\. Location: (?P<location>.*?)$"
        )
    ]

    log_lines = read_file_with_fallback(log_file_path)
    lockpicking_logs = []
    mine_logs = []

    for line in log_lines:
        matched = False
        for pattern in lockpicking_patterns:
            match = pattern.match(line.strip())
            if match:
                log_entry = match.groupdict()

                # 提取位置并计算区块
                location = log_entry.get('location', '')
                coords = re.findall(r'[-]?\d+', location)
                if len(coords) >= 2:
                    x, y = int(coords[0]), int(coords[1])
                    zone = determine_zone(x, y)
                    log_entry['zone'] = zone  # 添加地区信息

                # 翻译锁类型
                lock_type = log_entry.get('lock_type', 'N/A')
                log_entry['lock_type'] = lock_type_translation.get(lock_type, lock_type)  # 翻译锁类型

                lockpicking_logs.append(log_entry)
                matched = True
                break
        if not matched:
            error_log = {'error': f"No match found for line: {line.strip()}"}
            lockpicking_logs.append(error_log)  # Assume unmatched logs are lockpicking logs for simplicity

    return lockpicking_logs, mine_logs

def populate_treeview(tree, logs):
    for log in logs:
        if 'error' not in log:
            tree.insert("", "end", values=list(log.values()))

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

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game Logs")

    log_file_path = "path_to_your_log_file.log"
    lockpicking_logs, mine_logs = parse_log_file(log_file_path)

    lockpicking_columns = ["timestamp", "player_name", "steam_id", "success", "elapsed_time", "failed_attempts", "target_object", "lock_type", "location", "zone"]
    mine_columns = ["timestamp", "player_name", "steam_id", "trap_name", "location"]

    lockpicking_tree = setup_logs_gui(root, lockpicking_columns, "Lockpicking Logs")
    populate_treeview(lockpicking_tree, lockpicking_logs)

    mine_tree = setup_logs_gui(root, mine_columns, "Mine Logs")
    populate_treeview(mine_tree, mine_logs)

    root.mainloop()
