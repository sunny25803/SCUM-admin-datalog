import os
from PyQt5.QtWidgets import QMessageBox, QComboBox, QLineEdit, QTabWidget, QRadioButton, QWidget, QTreeWidget
from config_handler import get_config_list, load_config, delete_config
from admin_logs_gui import setup_admin_logs_gui
from chat_logs_gui import setup_chat_logs_gui
from configs.trade_logs_handler import update_trade_logs
from kill_logs_gui import setup_kill_logs_gui
from login_logs_gui import setup_login_logs_gui
from violations_gui import setup_violations_gui
from lockpicking_gui import setup_lockpicking_logs_gui
from mine_gui import setup_mine_logs_gui  # 新增地雷日志导入
#from trade_logs_handler import update_trade_logs  # 新增交易日志导入

def update_config_menu(config_menu: QComboBox, selected_config: str):
    config_list = get_config_list()
    config_menu.clear()
    config_menu.addItems(config_list)
    if selected_config in config_list:
        config_menu.setCurrentText(selected_config)

def load_user_data(name: str, protocol_ftp: QRadioButton, protocol_sftp: QRadioButton, ftp_host_entry: QLineEdit, port_entry: QLineEdit, ftp_user_entry: QLineEdit, ftp_pass_entry: QLineEdit, game_port_entry: QLineEdit, 
                   admin_logs_tab: QWidget, chat_logs_tab: QWidget, kill_logs_tab: QWidget, login_logs_tab: QWidget, violations_tab: QWidget, lockpicking_logs_tab: QWidget, mine_logs_tab: QWidget, trade_tree: QTreeWidget):
    config = load_config(name)
    if config:
        protocol = config.get('protocol', 'FTP')
        if protocol == 'FTP':
            protocol_ftp.setChecked(True)
        else:
            protocol_sftp.setChecked(True)
        
        ftp_host_entry.setText(config.get('ftp_host', ''))
        port_entry.setText(str(config.get('port', '21')))
        ftp_user_entry.setText(config.get('ftp_user', ''))
        ftp_pass_entry.setText(config.get('ftp_pass', ''))
        game_port_entry.setText(config.get('game_port', ''))

        local_folder_path = os.path.join(os.getcwd(), f"{config.get('ftp_host')}_{config.get('game_port')}_Logs")
        if os.path.exists(local_folder_path):
            setup_admin_logs_gui(admin_logs_tab, local_folder_path)
            setup_chat_logs_gui(chat_logs_tab, local_folder_path)
            setup_kill_logs_gui(kill_logs_tab, local_folder_path)
            setup_login_logs_gui(login_logs_tab, local_folder_path)
            setup_violations_gui(violations_tab, local_folder_path)
            setup_lockpicking_logs_gui(lockpicking_logs_tab, local_folder_path)
            setup_mine_logs_gui(mine_logs_tab, local_folder_path)  # 新增地雷日志导入
            update_trade_logs(trade_tree, local_folder_path)  # 新增交易日志导入

def delete_selected_config(selected_config: QComboBox, config_menu: QComboBox):
    name = selected_config.currentText()
    if name:
        delete_config(name)
        update_config_menu(config_menu, name)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Configuration '{name}' deleted successfully.")
        msg.setWindowTitle("Success")
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("No configuration selected.")
        msg.setWindowTitle("Error")
        msg.exec_()
