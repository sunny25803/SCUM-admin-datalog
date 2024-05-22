import os
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
import math

from config_handler import get_full_path

class TabControl(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.expanded_width = 200
        self.collapsed_width = 80
        self.is_expanded = True
        self.tabs = {
            "主要设置": "main.png",
            "管理员日志": "manager.png",
            "聊天日志": "chat.png",
            "击杀日志": "kill.png",
            "登录日志": "login.png",
            "违规日志": "violation.png",
            "撬锁日志": "lockpick.png",
            "地雷日志": "mine.png",
            "交易日志": "trade.png"
        }
        self.tab_widgets = {}
        self.tab_texts = {}
        self.selected_tab_index = 1  # 默认选中第一个标签

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.NoFocus)  # 禁用焦点虚线框
        self.icon_button = QListWidgetItem()
        self.icon_button.setIcon(QIcon(get_full_path("icons/menu.png")))
        self.icon_button.setTextAlignment(Qt.AlignCenter)
        self.icon_button.setFlags(self.icon_button.flags() & ~Qt.ItemIsSelectable)  # 禁用菜单按钮的可选中状态
        self.list_widget.addItem(self.icon_button)

        self.main_layout.addWidget(self.list_widget)

        self.create_tabs()
        self.update_style()
        self.set_initial_state()

        # 初始化定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.perform_resize)
        self.animation_duration = 250  # 动画持续时间（毫秒）
        self.animation_steps = 144  # 动画步骤数
        self.current_step = 0
        self.start_width = self.expanded_width
        self.end_width = self.collapsed_width

    def create_tabs(self):
        """创建标签"""
        for index, (name, icon) in enumerate(self.tabs.items(), start=1):
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignCenter)
            item.setIcon(QIcon(get_full_path(f"icons/{icon}")))
            self.list_widget.addItem(item)
            tab_content = QWidget()
            self.stacked_widget.addWidget(tab_content)
            self.tab_widgets[name] = tab_content
            self.tab_texts[index] = name

        self.list_widget.itemClicked.connect(self.handle_tab_click)

    def update_style(self):
        """更新样式"""
        if self.is_expanded:
            border_radius = "25px"
            list_widget_style = f"""
                QListWidget {{
                    background-color: #333333;
                    color: white;
                    font-size: 18px;
                    border-radius: 25px;
                    margin: 10px;
                }}
                QListWidget::item {{
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 50px;
                    border-radius: {border_radius};
                    margin: 5px;
                    text-align: center;
                }}
                QListWidget::item:selected {{
                    background-color: white;
                    color: black;
                }}
                QListWidget::item:hover {{
                    background-color: #444444;
                }}
                QListWidget::item:selected:hover {{
                    background-color: white;
                    color: black;
                }}
                QListWidget::item:focus {{
                    outline: none;
                }}
                QListWidget::item:selected:focus {{
                    outline: none;
                }}
            """
        else:
            list_widget_style = f"""
                QListWidget {{
                    background-color: #333333;
                    color: white;
                    font-size: 18px;
                    border-top-left-radius: 25px;
                    border-top-right-radius: 25px;
                    border-bottom-left-radius: 25px;
                    border-bottom-right-radius: 25px;
                    margin: 10px;
                }}
                QListWidget::item {{
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 50px;
                    border-radius: 8px;
                    margin: 5px;
                    text-align: center;
                }}
                QListWidget::item:selected {{
                    background-color: white;
                    color: black;
                }}
                QListWidget::item:hover {{
                    background-color: #444444;
                }}
                QListWidget::item:selected:hover {{
                    background-color: white;
                    color: black;
                }}
                QListWidget::item:focus {{
                    outline: none;
                }}
                QListWidget::item:selected:focus {{
                    outline: none;
                }}
            """

        self.list_widget.setStyleSheet(list_widget_style)

    def handle_tab_click(self, item):
        """处理标签点击"""
        if item == self.icon_button:
            self.toggle_tabs(preserve_selection=True)
        else:
            index = self.list_widget.row(item)
            self.selected_tab_index = index  # 记录选中的标签索引
            self.stacked_widget.setCurrentIndex(index - 1)

    def toggle_tabs(self, preserve_selection=False):
        """切换标签显示/隐藏"""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            for i in range(1, self.list_widget.count()):
                item = self.list_widget.item(i)
                item.setText(self.tab_texts[i])
            self.icon_button.setText("菜单")
            self.start_width = self.collapsed_width
            self.end_width = self.expanded_width
        else:
            for i in range(1, self.list_widget.count()):
                item = self.list_widget.item(i)
                item.setText("")
            self.icon_button.setText("")
            self.start_width = self.expanded_width
            self.end_width = self.collapsed_width
        self.update_style()
        self.start_resize_animation()

        # 保持当前选中状态，确保菜单按钮不会被选中
        if preserve_selection:
            self.list_widget.setCurrentRow(self.selected_tab_index)

    def start_resize_animation(self):
        """开始调整大小的动画"""
        self.current_step = 0
        interval = self.animation_duration // self.animation_steps
        self.timer.start(interval)

    def perform_resize(self):
        """执行调整大小的动画步骤"""
        self.current_step += 1
        if self.current_step <= self.animation_steps:
            t = self.current_step / self.animation_steps
            easing_value = 0.5 * (1 - math.cos(math.pi * t))  # 正弦缓动函数
            width = self.start_width + (self.end_width - self.start_width) * easing_value
            self.setFixedWidth(int(width))
        else:
            self.timer.stop()
            self.setFixedWidth(self.end_width)

    def set_initial_state(self):
        """设置初始状态为展开状态"""
        for i in range(1, self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setText(self.tab_texts[i])
        self.setFixedWidth(self.expanded_width)
        self.icon_button.setText("菜单")
        self.update_style()
        self.list_widget.setCurrentRow(self.selected_tab_index)  # 设置初始选中状态
