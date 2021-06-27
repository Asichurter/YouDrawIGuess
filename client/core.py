from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
import time
import socket
import sys

from client.engine import ClientEngine
from client.signal import ClientSignal
from client.comp.LoginPanel import LoginPanel
from client.handlers import get_handler, check_game_is_end, check_game_is_begin
from vals.state import *
from log import GlobalLogger as logger
import config

addr = (config.connect.ServerAddr, config.connect.ServerMapPort)
# addr = ('127.0.0.1', 7890)

class Client:

    def __init__(self):
        self.Engine = None
        self.Signals = None
        self.GameThread = GameThread(self)


    def init_slots(self):
        self.Signals.bind_exit_signal(self.exit)


    # 激活状态，登录成功后的状态
    # 主要做游戏开始前的前置准备工作
    def activate(self, socket_obj, id_, usrname):
        try:
            self.Signals = ClientSignal()
            self.init_slots()
            self.Engine = ClientEngine(self.Signals, socket_obj)
            self.Engine.set_gamer_name_id(id_, usrname)
            logger.info('client.activate',
                        'activating...')

            cmd, gamers = self.Engine.recv_cmd()
            while cmd != 'GamerInfo':
                time.sleep(1)           # 忽略其他指令
                cmd, gamers = self.Engine.recv_cmd()

            for gname, gscore in gamers['gamers']:
                self.Engine.add_gamer(gname)

            # 启动一个额外的线程用于background任务
            self.GameThread.start()
            self.Engine.show()

        except Exception as e:
            logger.critical('client.core.activate',
                            'Err when activate: {}'.format(e))
            raise e


    def wait_for_ready(self):
        while True:
            try:
                cmd, vals = self.Engine.recv_cmd()
                logger.debug('client.core.wait_for_ready',
                            'recv cmd: {}, {}'.format(cmd, vals))

                handler = get_handler(C_WAIT_FOR_READY_STATE, cmd)
                ret = handler(self.Engine, self.Signals, **vals)
                if ret is not None and check_game_is_begin(ret):
                    break
            except Exception as e:
                logger.error('client.core.activate',
                             'err when handling, cmd: {}, vals: {}, err: {}'
                             .format(cmd, vals, e))

        self.game()

    def game(self):
        while True:
            try:
                cmd, vals = self.Engine.recv_cmd()

                logger.info('client.core.game',
                            f'cmd: {cmd}, vals: {vals}')

                handler = get_handler(C_GAME_STATE, cmd)
                ret = handler(self.Engine, self.Signals, **vals)
                if ret is not None and check_game_is_end(ret):
                    break

                logger.info('client.core.game',
                            f'cmd: {cmd} executed')

            except BaseException as e:
                logger.error('client.core.game',
                             'err when game: {}'.format(e))

        self.exit()


    # 绑定的退出的回调函数
    def exit(self):
        self.Engine.WelcomeSocket.close()
        self.GameThread.exit(0)


class GameThread(core.QThread):
    trigger = core.pyqtSignal()

    def __init__(self, client, **kwargs):
        super(GameThread, self).__init__(**kwargs)
        self.Client = client

    def run(self):
        self.Client.wait_for_ready()


if __name__ == '__main__':
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(addr)
    print('connecting...')

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)
    # get_messasge_box(None)
    game = Client()
    # game.activate(socket_, 0, 'test')
    login = LoginPanel(socket_, activator=game.activate)

    exit(app.exec_())  # 进入消息循环
