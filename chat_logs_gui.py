# chat_logs_gui.py
import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QHeaderView
from chat_logs import parse_chat_log_file
from PyQt5.QtCore import Qt

def setup_chat_logs_gui(tab: QWidget, local_folder_path: str):
    layout = QVBoxLayout(tab)
    chat_logs_tree = QTreeWidget()
    chat_logs_tree.setColumnCount(4)
    chat_logs_tree.setHeaderLabels(["时间戳", "玩家信息", "频道", "消息"])
    chat_logs_tree.setStyleSheet("""
        QTreeWidget {
            background-color: rgba(45, 45, 45, 0.45);  /* 设置背景颜色为45%透明 */
            color: white;
            font-size: 12px;
            border: 2px solid #4682B4;  /* 较深的蓝色 */
            border-radius: 20px;
            padding-right: 35px; /* 增加右边距，以便滚动条不会覆盖边框 */
        }
        QHeaderView::section {
            background-color: #4682B4;
            color: white;
            padding: 4px;
            border: 1px solid #4682B4;
            qproperty-alignment: AlignCenter; /* 中心对齐标题文本 */
            margin: 0px; /* 移除边距 */
        }
        QHeaderView {
            margin: 0px; /* 移除QHeaderView的边距 */
        }
        QTreeWidget::item {
            border: 1px solid #4682B4;
            padding: 4px;
        }
        QTreeWidget::item:hover {
            background-color: rgba(70, 130, 180, 0.8);  /* 透明度为80%的较深蓝色 */
            color: black;
        }
        QScrollBar:vertical {
            background: rgba(45, 45, 45, 0.68);  /* 设置背景颜色为68%透明 */
            width: 25px;  /* 滚动条宽度 */
            margin: 10px 10px 10px 0px;  /* 滚动条内边距，上下各减小10px */
            border: 1px solid #4682B4;  /* 边框颜色 */
            border-radius: 6px;  /* 滚动条边框圆角 */
        }
        QScrollBar::handle:vertical {
            background: #4682B4;  /* 滚动条滑块颜色 */
            min-height: 80px;  /* 滚动条滑块最小高度 */
            border-radius: 6px;  /* 滚动条滑块圆角 */
        }
        QScrollBar::handle:vertical:hover {
            background: #5a9bd3;  /* 滚动条滑块悬停颜色 */
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;  /* 删除上下两个按钮 */
            background: none;
        }
        QScrollBar::add-line:vertical:hover, QScrollBar::sub-line:vertical:hover {
            background: none;
        }
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            border: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """)
    layout.addWidget(chat_logs_tree)
    layout.setContentsMargins(0, 0, 10, 10)  # 设置布局的外边距，确保整体布局顶部有0像素距离，右侧和底部距离窗口边缘10像素

    header = chat_logs_tree.header()
    header.setDefaultAlignment(Qt.AlignCenter)
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(True)  # 允许自动拉伸最后一列

    chat_log_files = [f for f in os.listdir(local_folder_path) if f.startswith('chat_') and f.endswith('.log')]
    chat_log_entries = []
    for log_file in chat_log_files:
        chat_log_entries.extend(parse_chat_log_file(os.path.join(local_folder_path, log_file)))

    # 按时间戳从新到旧排序
    chat_log_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    chat_logs_tree.clear()
    if chat_log_entries:
        for entry in chat_log_entries:
            if 'error' in entry:
                continue
            timestamp = entry.get('timestamp', 'N/A')
            player_info = entry.get('player_name', 'N/A')
            channel = entry.get('channel', 'N/A')
            message = entry.get('message', 'N/A')
            item = QTreeWidgetItem([timestamp, player_info, channel, message])
            chat_logs_tree.addTopLevelItem(item)

    # 自动调整列宽，以确保时间戳列的内容能完整显示
    chat_logs_tree.resizeColumnToContents(0)
    
    tab.setLayout(layout)
    return chat_logs_tree
