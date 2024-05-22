import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt5.QtCore import Qt
from lockpicking import parse_log_file  # 改为导入 parse_log_file

def setup_lockpicking_logs_gui(tab: QWidget, local_folder_path: str):
    layout = QVBoxLayout(tab)
    lockpicking_tree = QTreeWidget()
    lockpicking_tree.setColumnCount(10)  # 更新列数以包含地区
    lockpicking_tree.setHeaderLabels(["时间戳", "玩家名称", "Steam ID", "成功", "用时", "失败尝试", "目标对象", "锁类型", "位置", "地区"])
    lockpicking_tree.setStyleSheet("""
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
    layout.addWidget(lockpicking_tree)
    layout.setContentsMargins(0, 0, 10, 10)  # 设置布局的外边距，确保整体布局顶部有0像素距离，右侧和底部距离窗口边缘10像素

    # 设置标题文字居中对齐
    header = lockpicking_tree.header()
    header.setDefaultAlignment(Qt.AlignCenter)

    # 保持允许手动调整列宽
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(True)  # 允许自动拉伸最后一列

    lockpicking_log_files = [f for f in os.listdir(local_folder_path) if f.startswith('gameplay_') and f.endswith('.log')]
    lockpicking_log_entries = []
    for log_file in lockpicking_log_files:
        lockpicking_logs, _ = parse_log_file(os.path.join(local_folder_path, log_file))
        lockpicking_log_entries.extend(lockpicking_logs)
    lockpicking_log_entries.sort(key=lambda x: x.get('timestamp', ''))

    lockpicking_tree.clear()
    if lockpicking_log_entries:
        for entry in lockpicking_log_entries:
            if 'error' in entry:
                continue
            timestamp = entry.get('timestamp', 'N/A')
            player_name = entry.get('player_name', 'N/A')
            steam_id = entry.get('steam_id', 'N/A')
            success = entry.get('success', 'N/A')
            elapsed_time = entry.get('elapsed_time', 'N/A')
            failed_attempts = entry.get('failed_attempts', 'N/A')
            target_object = entry.get('target_object', 'N/A')
            lock_type = entry.get('lock_type', 'N/A')
            location = entry.get('location', 'N/A')
            zone = entry.get('zone', 'N/A')  # 获取地区信息

            # 转换“成功”字段
            if success == 'Yes':
                success = '是'
            elif success == 'No':
                success = '否'

            item = QTreeWidgetItem([timestamp, player_name, steam_id, success, elapsed_time, failed_attempts, target_object, lock_type, location, zone])
            lockpicking_tree.addTopLevelItem(item)

    tab.setLayout(layout)
    return lockpicking_tree
