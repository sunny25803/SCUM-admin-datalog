import sys
from PyQt5.QtWidgets import QApplication, QDialog
from mainwindow import MainWindow  # 导入 MainWindow 类
from ui.loginmenu import LoginMenu  # 导入 LoginMenu 类

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_menu = LoginMenu()
    if login_menu.exec_() == QDialog.Accepted:
        mainWindow = MainWindow()
        mainWindow.show()
    sys.exit(app.exec_())
