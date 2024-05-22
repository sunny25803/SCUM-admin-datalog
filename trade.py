import re
from log_parser import read_file_with_fallback

def parse_trade_log_file(log_file_path):
    trade_patterns = [
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[Trade\] Tradeable \((?P<item>.*?) \(x(?P<quantity>\d+)\)\) purchased by (?P<player_name>.*?)\((?P<steam_id>\d+)\) for (?P<price>\d+) money from trader (?P<trader>.*?), old amount in store was (?P<old_amount>.*?), new amount is (?P<new_amount>.*?), and effective users online: (?P<users_online>\d+)"
        ),
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[Trade\] Before purchasing tradeables from trader (?P<trader>.*?), player (?P<player_name>.*?)\((?P<steam_id>\d+)\) had (?P<cash>\d+) cash, (?P<account_balance>\d+) account balance and (?P<gold>\d+) gold and trader had (?P<trader_funds>\d+) funds."
        ),
        re.compile(
            r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}): \[Trade\] After tradeable purchase from trader (?P<trader>.*?), player (?P<player_name>.*?)\((?P<steam_id>\d+)\) has (?P<cash>\d+) cash, (?P<account_balance>\d+) bank account balance and (?P<gold>\d+) gold and trader has (?P<trader_funds>\d+) funds."
        )
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
            trade_logs.append({'error': f"No match found for line: {line.strip()}"})

    return trade_logs

def get_trade_log_info(parsed_logs):
    info_list = []
    for log in parsed_logs:
        if 'error' in log:
            info_list.append(f"Error log: {log}")
        else:
            info_list.append(
                f"Time: {log['timestamp']}, Item: {log.get('item', 'N/A')} (x{log.get('quantity', 'N/A')}), "
                f"Player: {log['player_name']} (Steam ID: {log['steam_id']}), Price: {log.get('price', 'N/A')}, "
                f"Trader: {log.get('trader', 'N/A')}, Old Amount: {log.get('old_amount', 'N/A')}, "
                f"New Amount: {log['new_amount']}, Users Online: {log.get('users_online', 'N/A')}, "
                f"Cash: {log.get('cash', 'N/A')}, Account Balance: {log.get('account_balance', 'N/A')}, "
                f"Gold: {log.get('gold', 'N/A')}, Trader Funds: {log.get('trader_funds', 'N/A')}"
            )
    return "\n".join(info_list)

# Example usage
if __name__ == "__main__":
    log_file_path = "path_to_your_log_file.log"
    trade_logs = parse_trade_log_file(log_file_path)
    for log in trade_logs:
        print(log)
