import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QHeaderView, QMenu, QAction, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QEvent, QObject

from admin_logs import parse_admin_log_file

class HeaderEventFilter(QObject):
    def __init__(self, parent=None):
        super(HeaderEventFilter, self).__init__(parent)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            obj.setStyleSheet("background-color: #5a9bd3; color: white;")
        elif event.type() == QEvent.Leave:
            obj.setStyleSheet("background-color: #4682B4; color: white;")
        return super(HeaderEventFilter, self).eventFilter(obj, event)

def setup_admin_logs_gui(tab: QWidget, local_folder_path: str):
    layout = QVBoxLayout(tab)
    
    admin_logs_tree = QTreeWidget()
    admin_logs_tree.setColumnCount(4)
    admin_logs_tree.setHeaderLabels(["时间戳", "玩家信息", "命令", "参数"])
    admin_logs_tree.setStyleSheet("""
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
        QHeaderView::section:first {
            margin-left: 0px;  /* 调整时间戳按钮左侧对齐 */
        }
        QHeaderView::section:last {
            margin-right: 0px;  /* 调整最后一列按钮右侧对齐 */
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
        QTreeWidget::item:selected {
            background-color: white;  /* 选中项背景颜色 */
            color: black;  /* 选中项文本颜色 */
        }
        QScrollBar:vertical {
            background: rgba(45, 45, 45, 0.68);  /* 设置背景颜色为68%透明 */
            width: 25px;  /* 滚动条宽度 */
            margin: 10px 10px 10px 0px;  /* 滚动条内边距，上下各减小10px */
            border: 1px solid #4682B4;  /* 边框颜色 */
            border-radius: 6px;  /* 滋动条边框圆角 */
        }
        QScrollBar::handle:vertical {
            background: #4682B4;  /* 滋动条滑块颜色 */
            min-height: 80px;  /* 滋动条滑块最小高度 */
            border-radius: 6px;  /* 滋动条滑块圆角 */
        }
        QScrollBar::handle:vertical:hover {
            background: #5a9bd3;  /* 滋动条滑块悬停颜色 */
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

    layout.addWidget(admin_logs_tree)
    layout.setContentsMargins(0, 0, 10, 10)  # 设置布局的外边距，确保整体布局顶部有0像素距离，右侧和底部距离窗口边缘10像素

    # 设置标题文字居中对齐
    header = admin_logs_tree.header()
    header.setDefaultAlignment(Qt.AlignCenter)

    # 设置时间戳列的初始宽度
    timestamp_col_width = 150  # 可以根据需要调整宽度
    admin_logs_tree.setColumnWidth(0, timestamp_col_width)

    # 保持允许手动调整列宽
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(True)  # 允许自动拉伸最后一列

    # 动态调整滚动条和大框的边距
    def adjust_scrollbar_margin():
        scrollbar_width = admin_logs_tree.verticalScrollBar().width()
        admin_logs_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: rgba(45, 45, 45, 0.45);  /* 设置背景颜色为45%透明 */
                color: white;
                font-size: 12px;
                border: 2px solid #4682B4;  /* 较深的蓝色 */
                border-radius: 20px;
                padding-left: 10px; /* 增加左边距，以便大框与时间戳按钮保持距离 */
                padding-right: {scrollbar_width + 10}px; /* 动态调整右边距 */
            }}
            QHeaderView::section {{
                background-color: #4682B4;
                color: white;
                padding: 4px;
                border: 1px solid #4682B4;
                qproperty-alignment: AlignCenter; /* 中心对齐标题文本 */
                margin: 0px; /* 移除边距 */
            }}
            QHeaderView::section:first {{
                margin-left: 0px;  /* 调整时间戳按钮左侧对齐 */
            }}
            QHeaderView::section:last {{
                margin-right: 0px;  /* 调整最后一列按钮右侧对齐 */
            }}
            QHeaderView {{
                margin: 0px; /* 移除QHeaderView的边距 */
            }}
            QTreeWidget::item {{
                border: 1px solid #4682B4;
                padding: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: rgba(70, 130, 180, 0.8);  /* 透明度为80%的较深蓝色 */
                color: black;
            }}
            QTreeWidget::item:selected {{
                background-color: white;  /* 选中项背景颜色 */
                color: black;  /* 选中项文本颜色 */
            }}
            QScrollBar:vertical {{
                background: rgba(45, 45, 45, 0.68);  /* 设置背景颜色为68%透明 */
                width: 25px;  /* 滚动条宽度 */
                margin: 10px 10px 10px 0px;  /* 滋动条内边距，上下各减小10px */
                border: 1px solid #4682B4;  /* 边框颜色 */
                border-radius: 6px;  /* 滋动条边框圆角 */
            }}
            QScrollBar::handle:vertical {{
                background: #4682B4;  /* 滋动条滑块颜色 */
                min-height: 80px;  /* 滋动条滑块最小高度 */
                border-radius: 6px;  /* 滋动条滑块圆角 */
            }}
            QScrollBar::handle:vertical:hover {{
                background: #5a9bd3;  /* 滋动条滑块悬停颜色 */
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;  /* 删除上下两个按钮 */
                background: none;
            }}
            QScrollBar::add-line:vertical:hover, QScrollBar::sub-line:vertical:hover {{
                background: none;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

    adjust_scrollbar_margin()  # 调整初始边距
    admin_logs_tree.verticalScrollBar().rangeChanged.connect(adjust_scrollbar_margin)  # 滋动条范围变化时调整边距

    # 悬停事件处理
    header_event_filter = HeaderEventFilter()
    header.installEventFilter(header_event_filter)

    log_files = [f for f in os.listdir(local_folder_path) if f.startswith('admin_') and f.endswith('.log')]
    admin_log_entries = []
    for log_file in log_files:
        admin_log_entries.extend(parse_admin_log_file(os.path.join(local_folder_path, log_file)))
    
    # 按时间戳从新到旧排序
    admin_log_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    admin_logs_tree.clear()
    if admin_log_entries:
        for entry in admin_log_entries:
            if 'error' in entry:
                continue
            timestamp = entry.get('timestamp', 'N/A')
            player_info = f"{entry.get('player_name', 'N/A')} ({entry.get('player_number', 'N/A')})"
            command = entry.get('command', 'N/A')
            parameters = entry.get('parameters', 'N/A')
            item = QTreeWidgetItem([timestamp, player_info, command, parameters])
            item.setFlags(item.flags() | Qt.ItemIsEditable)  # 设置为可编辑
            admin_logs_tree.addTopLevelItem(item)

    # 添加上下文菜单
    admin_logs_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    admin_logs_tree.customContextMenuRequested.connect(lambda pos: on_context_menu(pos, admin_logs_tree, local_folder_path))

    tab.setLayout(layout)

    return admin_logs_tree

def on_context_menu(pos, tree_widget, local_folder_path):
    menu = QMenu(tree_widget)
    menu.setStyleSheet("""
        QMenu {
            background-color: white;  /* 右键菜单背景颜色 */
            color: black;  /* 右键菜单文字颜色 */
        }
        QMenu::item {
            background-color: white;  /* 右键菜单项背景颜色 */
            color: black;  /* 右键菜单项文字颜色 */
        }
        QMenu::item:selected {
            background-color: lightblue;  /* 右键菜单项悬停背景颜色 */
            color: blue;  /* 右键菜单项悬停文字颜色 */
        }
    """)
    edit_action = QAction("修改", tree_widget)
    edit_action.triggered.connect(lambda: edit_selected_item(tree_widget, local_folder_path))
    menu.addAction(edit_action)
    copy_action = QAction("复制", tree_widget)
    copy_action.triggered.connect(lambda: copy_selected_items(tree_widget))
    menu.addAction(copy_action)
    menu.exec_(tree_widget.mapToGlobal(pos))

def copy_selected_items(tree_widget):
    selected_items = tree_widget.selectedItems()
    if not selected_items:
        return
    clipboard = QApplication.clipboard()
    text_to_copy = ""
    for item in selected_items:
        row_data = [item.text(column) for column in range(tree_widget.columnCount())]
        text_to_copy += "\t".join(row_data) + "\n"
    clipboard.setText(text_to_copy)

def edit_selected_item(tree_widget, local_folder_path):
    selected_items = tree_widget.selectedItems()
    if not selected_items:
        return
    item = selected_items[0]

    # 启动编辑模式
    for column in range(tree_widget.columnCount()):
        tree_widget.editItem(item, column)

    # 获取修改后的内容
    timestamp = item.text(0)
    player_info = item.text(1)
    command = item.text(2)
    parameters = item.text(3)

    # 显示提示信息
    show_warning_dialog("修改功能有可能导致未刷新的日志丢失，建议您在修改前手动更新日志文件。")

    # 将修改后的内容写回日志文件
    try:
        source_file = None
        original_entry = None
        log_files = [f for f in os.listdir(local_folder_path) if f.startswith('admin_') and f.endswith('.log')]
        for log_file in log_files:
            log_entries = parse_admin_log_file(os.path.join(local_folder_path, log_file))
            for entry in log_entries:
                if entry.get('timestamp') == timestamp and entry.get('player_name') == item.text(1).split(' (')[0]:
                    source_file = entry['source_file']
                    original_entry = entry
                    break
            if source_file:
                break

        if source_file and original_entry:
            # 更新原始日志条目的内容
            player_info_split = player_info.split(' (')
            if len(player_info_split) == 2:
                original_entry['player_name'], original_entry['player_number'] = player_info_split[0], player_info_split[1][:-1]
            original_entry['command'] = command
            original_entry['parameters'] = parameters

            # 读取原始日志文件并更新指定行
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(source_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    if original_entry['timestamp'] in line and original_entry['player_name'] in line:
                        # 替换旧的日志条目
                        new_line = f"{original_entry.get('timestamp', 'N/A')} {original_entry.get('player_name', 'N/A')} ({original_entry.get('player_number', 'N/A')}) {original_entry.get('command', 'N/A')} {original_entry.get('parameters', 'N/A')}\n"
                        f.write(new_line)
                    else:
                        f.write(line)
            
            show_warning_dialog("日志文件修改成功。")
        else:
            raise Exception("未找到对应的日志文件或日志条目")
    except Exception as e:
        print(f"修改日志文件失败: {e}")
        show_warning_dialog("日志文件修改失败。")

def save_admin_log_file(file_path, log_entries):
    with open(file_path, 'w', encoding='utf-8') as f:  # 确保以utf-8编码写入文件
        for entry in log_entries:
            line = f"{entry.get('timestamp', 'N/A')} {entry.get('player_name', 'N/A')} ({entry.get('player_number', 'N/A')}) {entry.get('command', 'N/A')} {entry.get('parameters', 'N/A')}\n"
            f.write(line)

def show_warning_dialog(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("警告")
    msg_box.setText(message)
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: white;
            color: black;
        }
        QMessageBox QLabel {
            color: black;
        }
        QMessageBox QPushButton {
            background-color: lightgray;
            color: black;
        }
        QMessageBox QPushButton:hover {
            background-color: gray;
        }
    """)
    msg_box.exec_()
