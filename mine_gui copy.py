# mine_gui.py
import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from mine import parse_mine_log_file  # 导入parse_mine_log_file

def setup_mine_logs_gui(tab: QWidget, local_folder_path: str):
    layout = QVBoxLayout(tab)
    mine_tree = QTreeWidget()
    mine_tree.setColumnCount(8)
    mine_tree.setHeaderLabels(["Timestamp", "Event", "Player Name", "Steam ID", "Trap Name", "Owner Name", "Owner Steam ID", "Location"])
    layout.addWidget(mine_tree)
    
    mine_log_files = [f for f in os.listdir(local_folder_path) if f.startswith('gameplay_') and f.endswith('.log')]
    mine_log_entries = []
    for log_file in mine_log_files:
        mine_logs = parse_mine_log_file(os.path.join(local_folder_path, log_file))
        mine_log_entries.extend(mine_logs)
    mine_log_entries.sort(key=lambda x: x.get('timestamp', ''))

    mine_tree.clear()
    if mine_log_entries:
        for entry in mine_log_entries:
            if 'error' in entry:
                continue
            timestamp = entry.get('timestamp', 'N/A')
            event = entry.get('event', 'N/A')
            player_name = entry.get('player_name', 'N/A')
            steam_id = entry.get('steam_id', 'N/A')
            trap_name = entry.get('trap_name', 'N/A')
            owner_name = entry.get('owner_name', 'N/A')
            owner_steam_id = entry.get('owner_steam_id', 'N/A')
            location = entry.get('location', 'N/A')
            item = QTreeWidgetItem([timestamp, event, player_name, steam_id, trap_name, owner_name, owner_steam_id, location])
            mine_tree.addTopLevelItem(item)

    tab.setLayout(layout)
    return mine_tree
