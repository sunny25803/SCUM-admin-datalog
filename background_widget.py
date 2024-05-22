# background_widget.py
import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from config_handler import get_base_path

class BackgroundWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None  # 初始化 pixmap 为 None
        self.initUI()

    def initUI(self):
        self.background_image_path = os.path.join(get_base_path(), 'background', 'background.png')
        if not os.path.exists(self.background_image_path):
            print(f"Background image not found at path: {self.background_image_path}")
            return
        
        self.pixmap = QPixmap(self.background_image_path)
        if self.pixmap.isNull():  # 检查 pixmap 是否有效
            print("Failed to load background image.")
            return

        self.setPixmap(self.pixmap)
        self.setScaledContents(True)

    def resizeEvent(self, event):
        if self.pixmap is None or self.pixmap.isNull():  # 如果 pixmap 为空或无效，则直接返回
            return
        
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.setPixmap(self.pixmap.scaled(self.size(), aspectRatioMode=1))
        super().resizeEvent(event)
