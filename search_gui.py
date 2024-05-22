import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, QApplication,
                             QListWidget, QLabel, QDialog, QHBoxLayout, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDateTime, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush

class TimeRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('选择时间')
        self.setFixedSize(800, 500)
        self.setStyleSheet("background-color: #2d2d2d; border-radius: 15px;")
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置为无边框窗口

        self.layout = QVBoxLayout(self)

        self.date_layout = QHBoxLayout()
        self.start_date_edit = QDateTimeEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet("""
            QDateTimeEdit {
                background-color: #3d3d3d;
                color: white;
                border-radius: 15px;
                padding: 10px;
                border: 2px solid transparent;
            }
            QDateTimeEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;  /* 垂直居中 */
                width: 25px;  /* 设置按钮宽度为25px */
                border: 1px solid #4682B4;
                background-color: #4682B4;
                border-top-right-radius: 15px;  /* 设置右上角圆角半径 */
                border-bottom-right-radius: 15px;  /* 设置右下角圆角半径 */
                margin: 0px;
            }
            QDateTimeEdit::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
            QDateTimeEdit::drop-down:pressed {
                background-color: #5a9bd3;
            }
        """)

        self.end_date_edit = QDateTimeEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet("""
            QDateTimeEdit {
                background-color: #3d3d3d;
                color: white;
                border-radius: 15px;
                padding: 10px;
                border: 2px solid transparent;
            }
            QDateTimeEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;  /* 垂直居中 */
                width: 25px;  /* 设置按钮宽度为25px */
                border: 1px solid #4682B4;
                background-color: #4682B4;
                border-top-right-radius: 15px;  /* 设置右上角圆角半径 */
                border-bottom-right-radius: 15px;  /* 设置右下角圆角半径 */
                margin: 0px;
            }
            QDateTimeEdit::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
            QDateTimeEdit::drop-down:pressed {
                background-color: #5a9bd3;
            }
        """)

        self.date_layout.addWidget(self.start_date_edit)
        self.date_layout.addWidget(self.end_date_edit)

        self.button_layout = QHBoxLayout()
        self.confirm_button = QPushButton('确定', self)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4682B4;
                color: white;
                border-radius: 7px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a9bd3;
            }
        """)
        self.confirm_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton('取消', self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 7px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)

        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.confirm_button)

        self.layout.addLayout(self.date_layout)
        self.layout.addLayout(self.button_layout)

        # 用于记录鼠标位置
        self.old_pos = self.pos()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

class SearchGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 搜索栏
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("输入搜索关键词...")
        layout.addWidget(self.search_bar)

        # 时间选择按钮
        self.time_range_button = QPushButton("选择时间", self)
        self.time_range_button.clicked.connect(self.show_time_range_dialog)
        layout.addWidget(self.time_range_button)

        # 搜索按钮
        self.search_button = QPushButton("搜索", self)
        self.search_button.clicked.connect(self.perform_search)
        layout.addWidget(self.search_button)

        # 结果列表
        self.results_list = QListWidget(self)
        layout.addWidget(self.results_list)

        # 状态标签
        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QWidget#SearchGUI {
                background-color: rgba(45, 45, 45, 0.3);
                border-radius: 15px;
            }
        """)
        self.setObjectName('SearchGUI')

    def show_time_range_dialog(self):
        dialog = TimeRangeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            start_time = dialog.start_date_edit.dateTime().toString("yyyy.MM.dd-HH.mm.ss")
            end_time = dialog.end_date_edit.dateTime().toString("yyyy.MM.dd-HH.mm.ss")
            self.time_range_button.setText(f"{start_time} - {end_time}")
            self.time_range_button.adjustSize()

    def perform_search(self):
        query = self.search_bar.text()
        time_range_text = self.time_range_button.text()

        # 如果时间区段按钮没有选择时间，则设为None
        if time_range_text == "选择时间":
            start_timestamp, end_timestamp = None, None
        else:
            start_timestamp, end_timestamp = time_range_text.split(" - ")

        if query or time_range_text != "选择时间":
            # 执行搜索和时间过滤逻辑
            self.results_list.clear()
            results = self.search_files(query, start_timestamp, end_timestamp)
            if results:
                self.results_list.addItems(results)
                self.status_label.setText(f"找到 {len(results)} 个结果")
            else:
                self.status_label.setText("未找到相关结果")
        else:
            self.status_label.setText("请输入搜索关键词或选择时间区段")

    def search_files(self, query, start_timestamp, end_timestamp):
        # 模拟搜索逻辑，这里可以根据实际需求进行实现
        # 例如，可以遍历某个文件夹，或从数据库中搜索数据
        # 这里返回一些示例数据
        example_files = ["file1.txt", "file2.txt", "file3.txt"]
        # 根据query进行筛选
        filtered_files = [file for file in example_files if query.lower() in file.lower()]
        # 如果时间戳有范围限制，则进一步筛选
        if start_timestamp and end_timestamp:
            # 模拟根据时间戳进行筛选
            # 实际中应根据文件的时间戳进行筛选
            filtered_files = [file for file in filtered_files if start_timestamp <= file <= end_timestamp]
        return filtered_files

if __name__ == '__main__':
    app = QApplication(sys.argv)
    search_gui = SearchGUI()
    search_gui.show()
    sys.exit(app.exec_())
