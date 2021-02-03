from PyQt5.QtWidgets import QApplication

import sys

from GamePanel import GamePanel
from config import DefaultConfigSet


def main():
    app = QApplication(sys.argv)
    game = GamePanel(DefaultConfigSet)
    # mainWidget = PaintPanel()  # 新建一个主界面
    # mainWidget.show()  # 显示主界面

    exit(app.exec_())  # 进入消息循环


if __name__ == '__main__':
    main()