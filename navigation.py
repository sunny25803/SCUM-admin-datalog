# navigation.py
import logging
from PyQt5.QtWidgets import QWidget

def switch_window(current_window: QWidget, new_window_class: type):
    try:
        current_window.close()
        new_window = new_window_class()
        new_window.show()
    except Exception as e:
        logging.error(f"切换窗口失败: {e}")
        raise
