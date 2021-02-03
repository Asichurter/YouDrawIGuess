from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core


class Client:

    def __init__(self):
        pass


    def activate(self, socket_, id, usrname):

        self.Socket = socket_
        print('in activate...')
        # self.warn()
        self.ID = int(id)
        self.UsrName = usrname

        # 主机才有开始游戏的按钮
        print('id:', id)
        if self.ID == 0:
            self.GameBeginBtn.setVisible(True)

        _, gamers = decode_msg(self.recv_cmd())
        for g in gamers.keys():
            self.addGamer(g)

        # get_messasge_box(self)
        # self.warn()

        self.GameThread = GameThread(self)
        self.GameThread.start()

        self.show()
        print('showing...')

class GameThread(core.QThread):
    trigger = core.pyqtSignal()

    def __init__(self, panel, **kwargs):
        super(GameThread, self).__init__(**kwargs)
        self.Panel = panel

    def run(self):
        self.Panel.wait_for_ready()
