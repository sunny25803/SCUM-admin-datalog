import re
import chardet
import json

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

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

def parse_log_file(log_file_path):
    pattern = re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): '(?P<player_id>\d{17}):(?P<player_name>.*?)\((?P<player_number>\d+)\)' Command: '(?P<command>\w+)\s*(?P<parameters>.*)'")

    log_lines = read_file_with_fallback(log_file_path)

    parsed_logs = []

    for line in log_lines:
        match = pattern.match(line.strip())
        if match:
            timestamp = match.group('timestamp')
            player_name = match.group('player_name')
            player_number = match.group('player_number')
            command = match.group('command')
            parameters = match.group('parameters')

            parsed_logs.append({
                'timestamp': timestamp,
                'player_name': player_name,
                'player_number': player_number,
                'command': command,
                'parameters': parameters
            })
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

def parse_chat_log_file(log_file_path):
    pattern = re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): '(\d{17}):(?P<player_name>.*?)\((?P<player_number>\d+)\)' '(?P<channel>\w+): (?P<message>.*)'")

    log_lines = read_file_with_fallback(log_file_path)

    parsed_logs = []

    for line in log_lines:
        match = pattern.match(line.strip())
        if match:
            timestamp = match.group('timestamp')
            player_name = match.group('player_name')
            channel = match.group('channel')
            message = match.group('message')

            parsed_logs.append({
                'timestamp': timestamp,
                'player_name': player_name,
                'channel': channel,
                'message': message
            })
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

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

            parsed_logs.append({
                'timestamp': timestamp,
                'victim': victim,
                'killer': killer,
                'weapon': weapon,
                'distance': distance,
                'server_location': server_location,
                'client_location': client_location,
                'event_status': "N/A"  # 默认值
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
                server_location = f"KillerLoc: {killer_info.get('ServerLocation')}, VictimLoc: {victim_info.get('ServerLocation')}"
                client_location = f"KillerLoc: {killer_info.get('ClientLocation')}, VictimLoc: {victim_info.get('ClientLocation')}"

                parsed_logs.append({
                    'timestamp': timestamp,
                    'victim': victim,
                    'killer': killer,
                    'weapon': weapon,
                    'distance': distance,
                    'server_location': server_location,
                    'client_location': client_location,
                    'event_status': "N/A"  # 默认值
                })
            except json.JSONDecodeError as e:
                parsed_logs.append({'error': f"JSON decode error: {e} for line: {line.strip()}"})
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

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

def parse_violation_log_file(log_file_path):
    patterns = [
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Total violations detected for user -> User: (?P<player_name>.*?) \((?P<player_id>\d+), (?P<steam_id>\d+)\), Type: (?P<violation>.*?), Count: (?P<details>\d+)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Ammo count violation detected for user -> Weapon: (?P<details>.*?), User: (?P<player_name>.*?) \((?P<player_id>\d+), Location: .+"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Total violations detected for user -> User: (?P<player_name>.*?) \((?P<player_id>\d+), Type: (?P<violation>.*?), Count: (?P<details>\d+)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): (?P<violation>.+?) detected -> (?P<details>.*?), User: (?P<player_name>.*?) \((?P<player_id>\d+),.*"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): AConZGameMode::KickPlayer: User id: '(?P<player_id>\d+)', Reason: (?P<violation>.+)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Game version: (?P<details>.+)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): (?P<violation>.+?) -> (?P<details>.*?), User: (?P<player_name>.*?) \((?P<player_id>\d+)\)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): (?P<violation>.+?): (?P<details>.+), User: (?P<player_name>.*?) \((?P<player_id>\d+)\)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Ammo count violation detected for user -> Weapon: (?P<details>.*?), User: (?P<player_name>.*?) \((?P<player_id>\d+), (?P<steam_id>\d+)\), Location: .+"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): Request character action violation detected -> User: (?P<player_name>.*?) \((?P<player_id>\d+), (?P<steam_id>\d+)\), Desc: (?P<details>.*?), Action: (?P<action>.*?), Server location: (?P<server_location>.*?), Client location: (?P<client_location>.*?), Distance: (?P<distance>.*)")
    ]

    log_lines = read_file_with_fallback(log_file_path)
    parsed_logs = []

    for line in log_lines:
        for pattern in patterns:
            match = pattern.match(line.strip())
            if match:
                parsed_logs.append(match.groupdict())
                break
        else:
            parsed_logs.append({'error': f"No match found for line: {line.strip()}"})

    return parsed_logs

def parse_lockpicking_log_file(log_file_path):
    patterns = [
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[LogMinigame\] \[.*?\] User: (?P<player_name>.*?) \(\d+, (?P<steam_id>\d{17})\)\. Success: (?P<success>Yes|No)\. Elapsed time: (?P<elapsed_time>[\d\.]+)\. Failed attempts: (?P<failed_attempts>\d+)\. Target object: (?P<target_object>.*?)\(ID: (?P<target_object_id>.*?)\)\. Lock type: (?P<lock_type>.*?)\. User owner: \d+\(\[(?P<user_owner_steam_id>\d{17})\] (?P<user_owner_name>.*?)\)\. Location: (?P<location>.*?)$"
        ),
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[LogMinigame\] \[.*?\] User: (?P<player_name>.*?) \(\d+, (?P<steam_id>\d{17})\)\. Success: (?P<success>Yes|No)\. Elapsed time: (?P<elapsed_time>[\d\.]+)\. Failed attempts: (?P<failed_attempts>\d+)\. Target object: (?P<target_object>.*?)\(ID: N/A\)\. Lock type: (?P<lock_type>.*?)\. User owner: N/A\. Location: (?P<location>.*?)$"
        )
    ]

    log_lines = read_file_with_fallback(log_file_path)
    parsed_logs = []

    for line in log_lines:
        matched = False
        for pattern in patterns:
            match = pattern.match(line.strip())
            if match:
                parsed_logs.append(match.groupdict())
                matched = True
                break
        if not matched:
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
                f"Server Loc: {log['server_location']}, Client Loc: {log['client_location']}, Event Status: {log['event_status']}"
            )
    return "\n".join(info_list)

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

def get_violation_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Player: {log['player_name']} ({log['player_id']}), "
                f"Violation: {log['violation']}, Details: {log['details']}"
            )
    return "\n".join(info_list)

def get_lockpicking_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Player: {log.get('player_name', 'N/A')} (Steam ID: {log.get('steam_id', 'N/A')}), "
                f"Success: {log['success']}, Elapsed Time: {log['elapsed_time']}s, Failed Attempts: {log['failed_attempts']}, "
                f"Target Object: {log['target_object']}, Lock Type: {log['lock_type']}, Location: {log['location']}"
            )
    return "\n".join(info_list)

def parse_mine_log_file(log_file_path):
    pattern = re.compile(
        r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[LogTrap\] (?P<event>Triggered|Armed)\. User: (?P<player_name>.*?) \(\d+, (?P<steam_id>\d{17})\)\. Trap name: (?P<trap_name>.*?)\. (Owner: (?P<owner_name>.*?) \(\d+, (?P<owner_steam_id>\d{17})\)\. )?Location: (?P<location>.*?)$"
    )

    log_lines = read_file_with_fallback(log_file_path)
    mine_logs = []

    for line in log_lines:
        match = pattern.match(line.strip())
        if match:
            mine_logs.append(match.groupdict())
        else:
            mine_logs.append({'error': f"No match found for line: {line.strip()}"})

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
                f"Location: {log['location']}"
            )
    return "\n".join(info_list)

# 新增解析交易日志的函数
def parse_trade_log_file(log_file_path):
    trade_patterns = [
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[Trade\] Tradeable \((?P<item>.*?) \(x(?P<quantity>\d+)\)\) purchased by (?P<player_name>.*?)\((?P<steam_id>\d+)\) for (?P<price>\d+) money from trader (?P<trader>.*?), old amount in store was (?P<old_amount>.*?), new amount is (?P<new_amount>.*?), and effective users online: (?P<online_users>\d+)"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[Trade\] Before purchasing tradeables from trader (?P<trader>.*?), player (?P<player_name>.*?)\((?P<steam_id>\d+)\) had (?P<cash>\d+) cash, (?P<account_balance>\d+) account balance and (?P<gold>\d+) gold and trader had (?P<trader_funds>\d+) funds"),
        re.compile(r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[Trade\] After tradeable purchase from trader (?P<trader>.*?), player (?P<player_name>.*?)\((?P<steam_id>\d+)\) has (?P<cash>\d+) cash, (?P<account_balance>\d+) bank account balance and (?P<gold>\d+) gold and trader has (?P<trader_funds>\d+) funds")
    ]

    log_lines = read_file_with_fallback(log_file_path)
    trade_logs = []

    for line in log_lines:
        matched = False
        for pattern in trade_patterns:
            match = pattern.match(line.strip())
            if match:
                trade_logs.append(match.groupdict())
                matched = True
                break
        if not matched:
            trade_logs.append({'操': f"No match found for line: {line.strip()}"})

    return trade_logs

def get_trade_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            if 'item' in log:
                info_list.append(
                    f"Time: {log['timestamp']}, Item: {log['item']} (x{log['quantity']}), Player: {log['player_name']} (Steam ID: {log['steam_id']}), "
                    f"Price: {log['price']} money, Trader: {log['trader']}, Old Amount: {log['old_amount']}, New Amount: {log['new_amount']}, Online Users: {log['online_users']}"
                )
            else:
                info_list.append(
                    f"Time: {log['timestamp']}, Player: {log['player_name']} (Steam ID: {log['steam_id']}), "
                    f"Cash: {log['cash']}, Account Balance: {log['account_balance']}, Gold: {log['gold']}, Trader Funds: {log['trader_funds']}"
                )
    return "\n".join(info_list)
