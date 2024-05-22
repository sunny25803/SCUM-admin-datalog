from PyQt5.QtWidgets import QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu, QWidget, QHeaderView
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt

class TradeLogsUI:
    def __init__(self):
        self.trade_tree = None
        self.current_highlighted_item = None
        self.original_items = []

    def setup_trade_logs_gui(self, tab: QWidget):
        layout = QVBoxLayout(tab)
        self.trade_tree = QTreeWidget()
        self.trade_tree.setColumnCount(14)
        self.trade_tree.setHeaderLabels([
            "时间戳", "物品", "数量", "玩家名称", "Steam ID", "价格", "交易员", 
            "旧金额", "新金额", "在线用户", "现金", "账户余额", "金币", "交易员资金"
        ])
        self.trade_tree.setStyleSheet("""
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
        layout.addWidget(self.trade_tree)
        layout.setContentsMargins(0, 0, 10, 10)  # 设置布局的外边距，确保整体布局顶部有0像素距离，右侧和底部距离窗口边缘10像素
        tab.setLayout(layout)

        # 设置标题文字居中对齐
        header = self.trade_tree.header()
        header.setDefaultAlignment(Qt.AlignCenter)

        # 保持允许手动调整列宽
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)  # 允许自动拉伸最后一列

        self.trade_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.trade_tree.customContextMenuRequested.connect(self.open_context_menu)
        self.trade_tree.itemClicked.connect(self.on_trade_item_clicked)

    def open_context_menu(self, position):
        menu = QMenu()
        restore_action = menu.addAction("恢复原始顺序")
        restore_action.triggered.connect(self.restore_trade_tree_items)
        menu.exec_(self.trade_tree.viewport().mapToGlobal(position))

    def on_trade_item_clicked(self, item, column):
        if self.current_highlighted_item and self.current_highlighted_item == (item, column):
            self.restore_trade_tree_items()
            self.current_highlighted_item = None
        else:
            self.highlight_and_bring_to_top(item, column)

    def highlight_and_bring_to_top(self, item, column):
        text = item.text(column)
        self.restore_trade_tree_items()
        self.current_highlighted_item = (item, column)
        matching_items = []

        for i in range(self.trade_tree.topLevelItemCount()):
            top_item = self.trade_tree.topLevelItem(i)
            if top_item.text(column) == text:
                matching_items.append(top_item)

        for i, matching_item in enumerate(matching_items):
            self.trade_tree.takeTopLevelItem(self.trade_tree.indexOfTopLevelItem(matching_item))
            self.trade_tree.insertTopLevelItem(i, matching_item)

        for matching_item in matching_items:
            for j in range(matching_item.columnCount()):
                if j == column:
                    matching_item.setBackground(j, QBrush(Qt.yellow))
                    matching_item.setForeground(j, QBrush(QColor(255, 215, 0)))
                else:
                    matching_item.setBackground(j, QBrush(Qt.transparent))
                    matching_item.setForeground(j, QBrush(Qt.white))

    def restore_trade_tree_items(self):
        for i in range(self.trade_tree.topLevelItemCount()):
            top_item = self.trade_tree.topLevelItem(i)
            for j in range(top_item.columnCount()):
                top_item.setBackground(j, QBrush(Qt.transparent))
                top_item.setForeground(j, QBrush(Qt.white))

        self.trade_tree.clear()
        for item in self.original_items:
            self.trade_tree.addTopLevelItem(item.clone())

    def save_original_order(self):
        self.original_items = []
        for i in range(self.trade_tree.topLevelItemCount()):
            top_item = self.trade_tree.topLevelItem(i)
            self.original_items.append(top_item.clone())
