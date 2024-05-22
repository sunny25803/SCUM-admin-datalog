import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QShortcut
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence
from qt_material import apply_stylesheet
from config_handler import get_base_path, set_working_directory
from configs.trade_logs_handler import update_trade_logs
from trade_logs_ui import TradeLogsUI
from head_gui import TabControl
from mainsetting import MainSettingUI
from utils import load_local_files  # 修改为读取本地文件的方法
from background_widget import BackgroundWidget
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
        self.timer.timeout.connect(self.refresh_logs)
        self.timer.start(120000)  # 每2分钟刷新一次

        self.remote_folder_path = ""
        self.maximized = False
        self.old_pos = None  # 用于实现拖拽功能的变量

        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.show_browse_engine)

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

        for widget in [self.main_widget, self.tab_widget, self.stacked_widget, self.tab_control]:
            widget.setStyleSheet("background: transparent;")

        self.centerOnScreen()
        self.add_window_controls()

    def add_window_controls(self):
        icon_folder = os.path.join(os.path.dirname(__file__), "icons")
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

        buttons = [
            ("minimize_icon.png", self.showMinimized),
            ("maximize_icon.png", self.toggleMaximized),
            ("close_icon.png", self.close)
        ]

        for icon, slot in buttons:
            btn = self.create_control_button(icon_folder, icon, slot, button_style)
            self.layout.addWidget(btn, alignment=Qt.AlignTop | Qt.AlignRight)

    def create_control_button(self, icon_folder, icon, slot, style):
        btn = QPushButton(self)
        btn.setIcon(QIcon(os.path.join(icon_folder, icon)))
        btn.setIconSize(QSize(32, 32))
        btn.setFlat(True)
        btn.setStyleSheet(style)
        btn.clicked.connect(slot)
        return btn

    def toggleMaximized(self):
        self.maximized = not self.maximized
        self.showNormal() if self.maximized else self.showMaximized()

    def resizeEvent(self, event):
        self.background_widget.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def centerOnScreen(self):
        screen_rect = QApplication.desktop().availableGeometry(QApplication.desktop().primaryScreen())
        window_rect = self.geometry()
        self.move(
            (screen_rect.width() - window_rect.width()) // 2,
            (screen_rect.height() - window_rect.height()) // 2
        )

    def refresh_logs(self):
        try:
            local_folder_path = os.path.join(os.getcwd(), f"{self.main_setting_ui.ftp_host_entry.text()}_{self.main_setting_ui.game_port_entry.text()}_Logs")
            if os.path.exists(local_folder_path):
                print(f"Logs refreshed from {local_folder_path}")
                self.update_all_logs(local_folder_path)
        except Exception as e:
            print(f"Failed to refresh logs: {e}")

    def update_all_logs(self, local_folder_path):
        update_trade_logs(self.trade_logs_ui.trade_tree, local_folder_path)
        self.trade_logs_ui.save_original_order()
        # 在这里添加更新其他日志的方法
        # 例如: self.update_admin_logs(local_folder_path)
        # self.update_chat_logs(local_folder_path)
        # self.update_kill_logs(local_folder_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def show_browse_engine(self):
        self.browse_engine.show_and_center()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
