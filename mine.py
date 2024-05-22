# mine.py
import re
from log_parser import read_file_with_fallback
from zone_determiner import determine_zone  # 导入区块计算函数

# 事件类型翻译字典
event_translation = {
    "Triggered": "触发",
    "Armed": "布设"
}

def parse_mine_log_file(log_file_path):
    mine_patterns = [
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[LogTrap\] (?P<event>Triggered|Armed)\. User: (?P<player_name>.*?) \(\d+, (?P<steam_id>\d{17})\)\. Trap name: (?P<trap_name>.*?)\. (Owner: (?P<owner_name>.*?) \(\d+, (?P<owner_steam_id>\d{17})\)\. )?Location: (?P<location>.*?)$"
        )
    ]

    log_lines = read_file_with_fallback(log_file_path)
    mine_logs = []

    for line in log_lines:
        matched = False
        for pattern in mine_patterns:
            match = pattern.match(line.strip())
            if match:
                log_entry = match.groupdict()

                # 翻译事件类型
                event = log_entry.get('event', 'N/A')
                log_entry['event'] = event_translation.get(event, event)  # 翻译事件类型

                # 提取位置并计算区块
                location = log_entry.get('location', '')
                coords = re.findall(r'[-]?\d+', location)
                if len(coords) >= 2:
                    x, y = int(coords[0]), int(coords[1])
                    zone = determine_zone(x, y)
                    log_entry['zone'] = zone  # 添加地区信息
                else:
                    log_entry['zone'] = "N/A"

                mine_logs.append(log_entry)
                matched = True
                break
        if not matched:
            error_log = {'error': f"No match found for line: {line.strip()}"}
            mine_logs.append(error_log)

    return mine_logs

def get_mine_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Event: {log['event']}, Player: {log['player_name']} (Steam ID: {log['steam_id']}), "
                f"Trap: {log['trap_name']}, Owner: {log.get('owner_name', 'N/A')} (Steam ID: {log.get('owner_steam_id', 'N/A')}), "
                f"Location: {log['location']}, Zone: {log['zone']}"
            )
    return "\n".join(info_list)

# Example usage
if __name__ == "__main__":
    log_file_path = "path_to_your_log_file.log"
    mine_logs = parse_mine_log_file(log_file_path)
    for log in mine_logs:
        print(log)
