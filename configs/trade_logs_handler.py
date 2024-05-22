import re
import os
from log_parser import read_file_with_fallback
from PyQt5.QtWidgets import QTreeWidgetItem


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

def update_trade_logs(trade_tree, local_folder_path):
    trade_log_files = [f for f in os.listdir(local_folder_path) if f.startswith('economy_') and f.endswith('.log')]
    trade_log_entries = []
    
    for log_file in trade_log_files:
        trade_logs = parse_trade_log_file(os.path.join(local_folder_path, log_file))
        trade_log_entries.extend(trade_logs)
    
    trade_log_entries.sort(key=lambda x: x.get('timestamp', ''))

    trade_tree.clear()
    if trade_log_entries:
        for entry in trade_log_entries:
            if 'error' in entry:
                continue
            timestamp = entry.get('timestamp', 'N/A')
            item = entry.get('item', 'N/A')
            quantity = entry.get('quantity', 'N/A')
            player_name = entry.get('player_name', 'N/A')
            steam_id = entry.get('steam_id', 'N/A')
            price = entry.get('price', 'N/A')
            trader = entry.get('trader', 'N/A')
            old_amount = entry.get('old_amount', 'N/A')
            new_amount = entry.get('new_amount', 'N/A')
            users_online = entry.get('users_online', 'N/A')
            cash = entry.get('cash', 'N/A')
            account_balance = entry.get('account_balance', 'N/A')
            gold = entry.get('gold', 'N/A')
            trader_funds = entry.get('trader_funds', 'N/A')
            tree_item = QTreeWidgetItem([timestamp, item, quantity, player_name, steam_id, price, trader, old_amount, new_amount, users_online, cash, account_balance, gold, trader_funds])
            trade_tree.addTopLevelItem(tree_item)
