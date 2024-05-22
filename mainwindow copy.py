import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt, QSize, QPoint
from PyQt5.QtGui import QIcon, QColor, QPalette, QMouseEvent
from qt_material import apply_stylesheet
from config_handler import get_base_path, set_working_directory
from configs.trade_logs_handler import update_trade_logs
from trade_logs_ui import TradeLogsUI
from head_gui import TabControl
from mainsetting import MainSettingUI
from utils import download_and_open_files
from background_widget import BackgroundWidget
from search_gui import SearchGUI
from qframelesswindow import FramelessMainWindow, TitleBar

class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCUM 数据可视化工具")
        self.setMinimumSize(1920, 1080)
        
        set_working_directory()
        print(f"Base path set to: {get_base_path()}")

        self.trade_logs_ui = TradeLogsUI()
        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_new_files)
        self.timer.start(180000)  # 每3分钟检查一次

        self.remote_folder_path = ""
        self.current_highlighted_item = None
        self.maximized = False

        # 用于实现拖拽功能的变量
        self.old_pos = None

    def initUI(self):
        self.setTitleBar(TitleBar(self))

        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)

        self.background_widget = BackgroundWidget(self)
        self.background_widget.lower()

        self.stacked_widget = QStackedWidget()
        self.tab_control = TabControl(self.stacked_widget)

        self.tab_layout = QVBoxLayout()
        self.tab_layout.addWidget(self.tab_control)

        self.tab_widget = QWidget()
        self.tab_widget.setLayout(self.tab_layout)

        self.layout.addWidget(self.tab_widget, 1)
        self.layout.addWidget(self.stacked_widget, 4)

        self.main_setting_ui = MainSettingUI(self.tab_control, self.trade_logs_ui)
        self.trade_logs_ui.setup_trade_logs_gui(self.tab_control.tab_widgets["交易日志"])

        self.main_setting_ui.update_config_list()

        self.search_gui = SearchGUI()
        self.stacked_widget.addWidget(self.search_gui)

        self.main_widget.setStyleSheet("background: transparent;")
        self.tab_widget.setStyleSheet("background: transparent;")
        self.stacked_widget.setStyleSheet("background: transparent;")
        self.tab_control.setStyleSheet("background: transparent;")

        self.centerOnScreen()

        icon_folder = os.path.join(os.path.dirname(__file__), "icons")

        # 添加样式表定义悬停效果
        button_style = """
        QPushButton {
            border: none;
            background-color: transparent;
        }
        QPushButton:hover {
            background-color: rgba(100, 100, 100, 100);
            border: 0px solid rgba(255, 255, 255, 150);
            border-radius: 6px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 50);
        }
        """

        self.minimize_btn = QPushButton(self)
        self.minimize_btn.setIcon(QIcon(os.path.join(icon_folder, "minimize_icon.png")))
        self.minimize_btn.setIconSize(QSize(32, 32))
        self.minimize_btn.setFlat(True)
        self.minimize_btn.setStyleSheet(button_style)  # 应用样式表
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.layout.addWidget(self.minimize_btn, alignment=Qt.AlignTop | Qt.AlignRight)

        self.maximize_btn = QPushButton(self)
        self.maximize_btn.setIcon(QIcon(os.path.join(icon_folder, "maximize_icon.png")))
        self.maximize_btn.setIconSize(QSize(32, 32))
        self.maximize_btn.setFlat(True)
        self.maximize_btn.setStyleSheet(button_style)  # 应用样式表
        self.maximize_btn.clicked.connect(self.toggleMaximized)
        self.layout.addWidget(self.maximize_btn, alignment=Qt.AlignTop | Qt.AlignRight)

        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(QIcon(os.path.join(icon_folder, "close_icon.png")))
        self.close_btn.setIconSize(QSize(32, 32))
        self.close_btn.setFlat(True)
        self.close_btn.setStyleSheet(button_style)  # 应用样式表
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn, alignment=Qt.AlignTop | Qt.AlignRight)

    def toggleMaximized(self):
        if self.maximized:
            self.showNormal()
            self.maximized = False
        else:
            self.showMaximized()
            self.maximized = True

    def resizeEvent(self, event):
        self.background_widget.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def centerOnScreen(self):
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        window_rect = self.geometry()
        self.move(int((screen_rect.width() - window_rect.width()) / 2), int((screen_rect.height() - window_rect.height()) / 2))

    def check_for_new_files(self):
        protocol = "FTP" if self.main_setting_ui.protocol_ftp.isChecked() else "SFTP"
        ftp_host = self.main_setting_ui.ftp_host_entry.text()
        ftp_user = self.main_setting_ui.ftp_user_entry.text()
        ftp_pass = self.main_setting_ui.ftp_pass_entry.text()
        port_text = self.main_setting_ui.port_entry.text()
        game_port = self.main_setting_ui.game_port_entry.text()
        remote_folder_path = self.remote_folder_path

        if not port_text.isdigit():
            print("Invalid port number")
            return

        port = int(port_text)

        try:
            local_folder_path = download_and_open_files(protocol, ftp_host, ftp_user, ftp_pass, port, game_port, remote_folder_path)
            if local_folder_path:
                print(f"New files downloaded to {local_folder_path}")
                update_trade_logs(self.trade_logs_ui.trade_tree, local_folder_path)
                self.trade_logs_ui.save_original_order()
        except Exception as e:
            print(f"Failed to check for new files: {e}")

    # 添加鼠标事件处理函数
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
