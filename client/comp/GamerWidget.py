from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core

class GamerWidget(widgets.QWidget):
    def __init__(self, name='', point=0, visible=False):
        super(GamerWidget, self).__init__()

        layout = widgets.QVBoxLayout()
        layout.setAlignment(core.Qt.AlignLeft | core.Qt.AlignTop)

        self.GamerName = name
        self.NameLabel = widgets.QLabel(self.GamerName)
        self.GamerPoint = point
        self.PointLabel = widgets.QLabel(str(self.GamerPoint))
        layout.addWidget(self.NameLabel)
        layout.addWidget(self.PointLabel)

        self.setLayout(layout)
        # self.setVisible(visible)
        self.NameLabel.setVisible(visible)
        self.PointLabel.setVisible(visible)

    def set_name(self, name):
        self.GamerName = name
        self.NameLabel.setText(name)

        # 改变名字的时候将该玩家可见
        # self.setVisible(True)
        self.NameLabel.setVisible(True)
        self.PointLabel.setVisible(True)

    def set_point(self, point):
        self.GamerPoint = point
        self.PointLabel.setText(point)


