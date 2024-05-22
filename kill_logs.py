import tkinter as tk
from tkinter import ttk
import re
import json
from log_parser import read_file_with_fallback
from zone_determiner import determine_zone  # 导入区块计算函数

def setup_kill_logs_gui(parent):
    columns = ("timestamp", "victim", "killer", "weapon", "distance", "server_location", "client_location", "zone")
    tree = ttk.Treeview(parent, columns=columns, show='headings')
    tree.heading("timestamp", text="时间")
    tree.heading("victim", text="受害者")
    tree.heading("killer", text="击杀者")
    tree.heading("weapon", text="武器")
    tree.heading("distance", text="距离")
    tree.heading("server_location", text="服务器位置")
    tree.heading("client_location", text="客户端位置")
    tree.heading("zone", text="区域")
    tree.pack(fill="both", expand=True)
    return tree

def parse_kill_log_file(log_file_path):
    pattern1 = re.compile(
        r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Died: (?P<victim>.*?) \(\d{17}\), Killer: (?P<killer>.*?) \(\d{17}\) Weapon: (?P<weapon>.*?) "
        r"S\[KillerLoc : (?P<killer_loc>.*?), VictimLoc: (?P<victim_loc>.*?), Distance: (?P<distance>.*?) m\] "
        r"C\[KillerLoc: (?P<client_killer_loc>.*?), VictimLoc: (?P<client_victim_loc>.*?), Distance: (?P<client_distance>.*?) m\]"
    )

    pattern2 = re.compile(
        r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): (?P<data>\{.*\})"
    )

    log_lines = read_file_with_fallback(log_file_path)

    parsed_logs = []

    for line in log_lines:
        match1 = pattern1.match(line.strip())
        match2 = pattern2.match(line.strip())
        if match1:
            timestamp = match1.group('timestamp')
            victim = match1.group('victim')
            killer = match1.group('killer')
            weapon = match1.group('weapon')
            distance = match1.group('distance')
            server_location = f"KillerLoc: {match1.group('killer_loc')}, VictimLoc: {match1.group('victim_loc')}"
            client_location = f"KillerLoc: {match1.group('client_killer_loc')}, VictimLoc: {match1.group('client_victim_loc')}"

            # 提取服务器位置的KillerLoc的X和Y坐标并计算区域
            killer_loc_coords = re.findall(r'[-]?\d+', match1.group('killer_loc'))
            if len(killer_loc_coords) >= 2:
                x, y = int(killer_loc_coords[0]), int(killer_loc_coords[1])
                zone = determine_zone(x, y)
            else:
                zone = "N/A"

            parsed_logs.append({
                'timestamp': timestamp,
                'victim': victim,
                'killer': killer,
                'weapon': weapon,
                'distance': distance,
                'server_location': server_location,
                'client_location': client_location,
                'zone': zone  # 添加区域信息
            })
        elif match2:
            try:
                data = json.loads(match2.group('data'))
                killer_info = data.get('Killer', {})
                victim_info = data.get('Victim', {})
                timestamp = match2.group('timestamp')
                victim = victim_info.get('ProfileName')
                killer = killer_info.get('ProfileName')
                weapon = data.get('Weapon')
                distance = "N/A"
                
                server_location = killer_info.get('ServerLocation')
                if isinstance(server_location, dict):
                    server_location_str = f"KillerLoc: {server_location}, VictimLoc: {victim_info.get('ServerLocation')}"
                    killer_loc_coords = [server_location.get('X', 0), server_location.get('Y', 0)]
                else:
                    server_location_str = f"KillerLoc: {server_location}, VictimLoc: {victim_info.get('ServerLocation')}"
                    killer_loc_coords = re.findall(r'[-]?\d+', server_location)

                if len(killer_loc_coords) >= 2:
                    x, y = int(killer_loc_coords[0]), int(killer_loc_coords[1])
                    zone = determine_zone(x, y)
                else:
                    zone = "N/A"

                client_location = f"KillerLoc: {killer_info.get('ClientLocation')}, VictimLoc: {victim_info.get('ClientLocation')}"

                parsed_logs.append({
                    'timestamp': timestamp,
                    'victim': victim,
                    'killer': killer,
                    'weapon': weapon,
                    'distance': distance,
                    'server_location': server_location_str,
                    'client_location': client_location,
                    'zone': zone  # 添加区域信息
                })
            except json.JSONDecodeError as e:
                parsed_logs.append({'error': f"JSON decode error: {e} for line: {line.strip()}"})
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

def get_kill_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Victim: {log['victim']}, Killer: {log['killer']}, "
                f"Weapon: {log['weapon']}, Distance: {log['distance']}m, "
                f"Server Loc: {log['server_location']}, Client Loc: {log['client_location']}, Zone: {log['zone']}"
            )
    return "\n".join(info_list)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game Logs")

    log_file_path = "path_to_your_log_file.log"
    kill_logs = parse_kill_log_file(log_file_path)

    kill_logs_tree = setup_kill_logs_gui(root)
    for log in kill_logs:
        if 'error' not in log:
            kill_logs_tree.insert("", "end", values=list(log.values()))

    root.mainloop()
