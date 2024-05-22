import math
import os
from PyQt5.QtWidgets import QLabel, QComboBox, QRadioButton, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QFileDialog, QWidget, QGroupBox, QProgressDialog
from PyQt5.QtGui import QFont, QIcon
from config_handler import get_config_list, load_config, delete_config, save_config, get_full_path
from config_menu import load_user_data
from utils import download_and_open_files
from configs.trade_logs_handler import update_trade_logs
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(Exception)

    def __init__(self, protocol, ftp_host, ftp_user, ftp_pass, port, game_port, remote_folder_path):
        super().__init__()
        self.protocol = protocol
        self.ftp_host = ftp_host
        self.ftp_user = ftp_user
        self.ftp_pass = ftp_pass
        self.port = port
        self.game_port = game_port
        self.remote_folder_path = remote_folder_path

    def run(self):
        try:
            local_folder_path = download_and_open_files(self.protocol, self.ftp_host, self.ftp_user, self.ftp_pass, self.port, self.game_port, self.remote_folder_path)
            self.finished.emit(local_folder_path)
        except Exception as e:
            self.error.emit(e)

class MainSettingUI(QWidget):
    def __init__(self, tab_control, trade_logs_ui):
        super().__init__()
        self.tab_control = tab_control
        self.trade_logs_ui = trade_logs_ui
        self.remote_folder_path = ""  # 初始化 remote_folder_path
        self.initUI()

    def initUI(self):
        self.main_tab = self.tab_control.tab_widgets["主要设置"]
        self.main_layout = QGridLayout(self.main_tab)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self.group_box = QGroupBox("配置设置")
        self.group_box.setStyleSheet("""
            QGroupBox {
                background-color: rgba(51, 51, 51, 0.65);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.65);
                border-radius: 10px;
                margin-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
        """)
        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setContentsMargins(10, 20, 10, 10)
        self.group_layout.setSpacing(10)

        self.config_label = QLabel("选择配置:")
        self.config_label.setStyleSheet("color: white;")
        self.config_label.setFont(QFont("Arial", 14))
        self.group_layout.addWidget(self.config_label, 0, 0)

        self.selected_config = QComboBox()
        self.selected_config.setStyleSheet("""
            QComboBox {
                background-color: rgba(51, 51, 51, 0.65);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.65);
                border-radius: 8px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(51, 51, 51, 0.65);
                color: white;
                selection-background-color: rgba(255, 255, 255, 0.65);
            }
        """)
        self.group_layout.addWidget(self.selected_config, 0, 1, 1, 3)

        self.load_button = self.create_button("加载配置", "icons/load.png", self.load_config)
        self.group_layout.addWidget(self.load_button, 0, 4)

        self.delete_button = self.create_button("删除配置", "icons/delete.png", self.delete_config)
        self.group_layout.addWidget(self.delete_button, 0, 5)

        self.create_protocol_settings()
        self.create_ftp_settings()
        self.main_layout.addWidget(self.group_box, 0, 0, 1, 6)
        self.create_buttons()

    def create_protocol_settings(self):
        self.protocol_label = QLabel("协议:")
        self.protocol_label.setStyleSheet("color: white;")
        self.protocol_label.setFont(QFont("Arial", 14))
        self.group_layout.addWidget(self.protocol_label, 1, 0)

        self.protocol_ftp = QRadioButton("FTP")
        self.protocol_ftp.setStyleSheet("color: white;")
        self.protocol_ftp.setFont(QFont("Arial", 14))
        self.group_layout.addWidget(self.protocol_ftp, 1, 1)

        self.protocol_sftp = QRadioButton("SFTP")
        self.protocol_sftp.setStyleSheet("color: white;")
        self.protocol_sftp.setFont(QFont("Arial", 14))
        self.group_layout.addWidget(self.protocol_sftp, 1, 2)

    def create_ftp_settings(self):
        self.ftp_host_entry = self.add_label_and_entry("主机:", 2)
        self.port_entry = self.add_label_and_entry("端口:", 3)
        self.ftp_user_entry = self.add_label_and_entry("用户名:", 4)
        self.ftp_pass_entry = self.add_label_and_entry("密码:", 5, is_password=True)
        self.game_port_entry = self.add_label_and_entry("游戏端口:", 6)

        self.current_path_label = QLabel("当前远程路径: ")
        self.current_path_label.setStyleSheet("color: white;")
        self.current_path_label.setFont(QFont("Arial", 14))
        self.group_layout.addWidget(self.current_path_label, 7, 0, 1, 6)

    def add_label_and_entry(self, text, row, is_password=False):
        label = QLabel(text)
        label.setStyleSheet("color: white;")
        label.setFont(QFont("Arial", 14))
        self.group_layout.addWidget(label, row, 0)

        entry = QLineEdit()
        if is_password:
            entry.setEchoMode(QLineEdit.Password)
        entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(51, 51, 51, 0.65);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.65);
                border-radius: 8px;
                padding: 5px;
            }
        """)
        self.group_layout.addWidget(entry, row, 1, 1, 5)
        return entry

    def create_buttons(self):
        self.download_button = self.create_button("读取与存档", "icons/download.png", self.download_logs)
        self.main_layout.addWidget(self.download_button, 1, 0, 1, 6)

        self.save_button = self.create_button("保存数据", "icons/save.png", self.on_save_data)
        self.main_layout.addWidget(self.save_button, 2, 0, 1, 6)

        gg_pp_layout = QHBoxLayout()
        self.gg_host_button = self.create_button("GG 主机", None, self.set_gg_host)
        gg_pp_layout.addWidget(self.gg_host_button)

        self.pp_button = self.create_button("PP", None, self.set_pp)
        gg_pp_layout.addWidget(self.pp_button)

        gg_pp_widget = QWidget()
        gg_pp_widget.setLayout(gg_pp_layout)
        self.main_layout.addWidget(gg_pp_widget, 3, 0, 1, 6)

    def create_button(self, text, icon_path, callback):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(51, 51, 51, 0.65);
                color: white;
                border-radius: 20px;
                padding: 15px;
                font-size: 16px;
                min-width: 100px;  
                min-height: 40px;  
            }
            QPushButton:hover {
                background-color: rgba(68, 68, 68, 0.65);
            }
        """)
        if icon_path:
            button.setIcon(QIcon(get_full_path(icon_path)))
        button.clicked.connect(callback)
        return button

    def load_config(self):
        config_name = self.selected_config.currentText()
        config = load_config(config_name)
        if not config:
            QMessageBox.critical(self, "错误", f"未找到配置文件: {config_name}")
            return

        protocol = config.get('protocol', 'FTP')
        if protocol == "FTP":
            self.protocol_ftp.setChecked(True)
        else:
            self.protocol_sftp.setChecked(True)

        self.ftp_host_entry.setText(config.get('ftp_host', ''))
        self.port_entry.setText(str(config.get('port', '21')))
        self.ftp_user_entry.setText(config.get('ftp_user', ''))
        self.ftp_pass_entry.setText(config.get('ftp_pass', ''))
        self.game_port_entry.setText(config.get('game_port', ''))
        self.remote_folder_path = config.get('remote_folder_path', '')

        self.current_path_label.setText(f"当前远程路径: {self.remote_folder_path}")

        load_user_data(config_name, self.protocol_ftp, self.protocol_sftp, self.ftp_host_entry, self.port_entry, self.ftp_user_entry, self.ftp_pass_entry, self.game_port_entry,
                       self.tab_control.tab_widgets["管理员日志"], self.tab_control.tab_widgets["聊天日志"], self.tab_control.tab_widgets["击杀日志"], self.tab_control.tab_widgets["登录日志"], self.tab_control.tab_widgets["违规日志"], self.tab_control.tab_widgets["撬锁日志"], self.tab_control.tab_widgets["地雷日志"], self.trade_logs_ui.trade_tree)
        self.trade_logs_ui.save_original_order()

        self.download_logs()

    def delete_config(self):
        config_name = self.selected_config.currentText()
        delete_config(config_name)
        self.update_config_list()

    def download_logs(self):
        protocol = "FTP" if self.protocol_ftp.isChecked() else "SFTP"
        ftp_host = self.ftp_host_entry.text()
        ftp_user = self.ftp_user_entry.text()
        ftp_pass = self.ftp_pass_entry.text()
        port_text = self.port_entry.text()
        game_port = self.game_port_entry.text()
        remote_folder_path = self.remote_folder_path

        if not port_text.isdigit():
            QMessageBox.critical(self, "错误", "端口号必须是一个有效的整数")
            return

        port = int(port_text)

        self.progress_dialog = QProgressDialog("正在读取与下载，请稍候...", None, 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("请稍候")
        self.progress_dialog.show()

        self.download_thread = DownloadThread(protocol, ftp_host, ftp_user, ftp_pass, port, game_port, remote_folder_path)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def on_download_finished(self, local_folder_path):
        self.progress_dialog.close()
        if local_folder_path:
            QMessageBox.information(self, "成功", f"日志文件已下载到 {local_folder_path}")
            update_trade_logs(self.trade_logs_ui.trade_tree, local_folder_path)
            self.trade_logs_ui.save_original_order()

    def on_download_error(self, e):
        self.progress_dialog.close()
        QMessageBox.critical(self, "错误", str(e))

    def on_save_data(self):
        protocol = "FTP" if self.protocol_ftp.isChecked() else "SFTP"
        ftp_host = self.ftp_host_entry.text()
        ftp_user = self.ftp_user_entry.text()
        ftp_pass = self.ftp_pass_entry.text()
        port_text = self.port_entry.text()
        game_port = self.game_port_entry.text()
        remote_folder_path = self.remote_folder_path

        if not port_text.isdigit():
            QMessageBox.critical(self, "错误", "端口号必须是一个有效的整数")
            return

        port = int(port_text)

        save_path, _ = QFileDialog.getSaveFileName(self, "保存配置", "", "JSON 文件 (*.json)")
        if save_path:
            progress_dialog = QProgressDialog("正在保存数据，请稍候...", None, 0, 0, self)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setWindowTitle("请稍候")
            progress_dialog.show()

            name = os.path.splitext(os.path.basename(save_path))[0]
            config = {
                'protocol': protocol,
                'ftp_host': ftp_host,
                'ftp_user': ftp_user,
                'ftp_pass': ftp_pass,
                'port': port,
                'game_port': game_port,
                'remote_folder_path': remote_folder_path
            }
            save_config(name, config)
            self.update_config_list()
            progress_dialog.close()
            QMessageBox.information(self, "成功", "数据保存成功")

    def set_gg_host(self):
        self.protocol_sftp.setChecked(True)
        self.port_entry.setText("8822")

        ftp_host = self.ftp_host_entry.text()
        game_port = self.game_port_entry.text()

        if not game_port.isdigit():
            QMessageBox.critical(self, "错误", "游戏端口号必须是一个有效的整数")
            return

        remote_folder_path = f"/{ftp_host}_{game_port}/SaveFiles/Logs"
        self.remote_folder_path = remote_folder_path

        self.current_path_label.setText(f"当前远程路径: {self.remote_folder_path}")

    def set_pp(self):
        self.protocol_ftp.setChecked(True)
        self.port_entry.setText("8821")

        ftp_host = self.ftp_host_entry.text()
        game_port = self.game_port_entry.text()

        if not game_port.isdigit():
            QMessageBox.critical(self, "错误", "游戏端口号必须是一个有效的整数")
            return

        remote_folder_path = f"/{ftp_host}_{game_port}"
        self.remote_folder_path = remote_folder_path

        self.current_path_label.setText(f"当前远程路径: {self.remote_folder_path}")

    def update_config_list(self):
        config_list = get_config_list()
        print(f"Config list: {config_list}")
        self.selected_config.clear()
        self.selected_config.addItems(config_list)
