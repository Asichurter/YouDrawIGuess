from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core

from utils.style_utils import get_font_stylesheet

class GamerWidget(widgets.QWidget):
    PointStrTemp = '分数: {}'
    def __init__(self, name='', point=0, visible=False):
        super(GamerWidget, self).__init__()

        layout = widgets.QVBoxLayout()
        layout.setAlignment(core.Qt.AlignLeft | core.Qt.AlignTop)

        self.GamerName = name
        self.NameLabel = widgets.QLabel(self.GamerName)
        self.GamerPoint = point
        self.PointLabel = widgets.QLabel(self._get_point_str(self.GamerPoint))
        self.NameLabel.setStyleSheet(get_font_stylesheet(color=(30,120,255),size=20))   # 浅蓝色姓名
        self.PointLabel.setStyleSheet(get_font_stylesheet(color=(0,0,0),size=18))       # 黑色分数
        # self.NameLabel.setMaximumWidth(100)
        layout.addWidget(self.NameLabel)
        layout.addWidget(self.PointLabel)

        self.setLayout(layout)
        # self.setVisible(visible)
        self.NameLabel.setVisible(visible)
        self.PointLabel.setVisible(visible)

    def _get_point_str(self, point):
        return self.PointStrTemp.format(point)

    def set_name(self, name):
        self.GamerName = name
        self.NameLabel.setText(name)

        # 改变名字的时候将该玩家可见
        # self.setVisible(True)
        self.NameLabel.setVisible(True)
        self.PointLabel.setVisible(True)

    def set_point(self, point):
        self.GamerPoint = point
        point_str = self._get_point_str(point)
        self.PointLabel.setText(point_str)


