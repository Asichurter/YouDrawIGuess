import time
from threading import Lock
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core

from com.talk import send_cmd, recv_cmd
from client.signal import ClientSignal
from client.panel import GamePanel
from vals.command import *
import config

from log import GlobalLogger as logger


class ClientEngine:

    def __init__(self,
                 signals: ClientSignal,
                 socket_obj):

        self.Socket = socket_obj
        # 待发送的点临时buffer
        self.PointBuffer = []
        # 临时区锁
        self.BufferLock = Lock()
        # 客户端事件信号
        self.Signals = signals
        self.GameEndFlag = False

        self.GamerId = None
        self.GamerUsrName = None

        self.init_slots()
        self.Panel = GamePanel(self.Signals)  # todo: 修改panel


    def init_slots(self):
        self.Signals.bind_paint_point_signal(self.signal_paint_point)
        self.Signals.bind_click_point_signal(self.signal_click_point)
        self.Signals.bind_release_point_signal(self.signal_release_point)
        self.Signals.bind_chat_send_signal(self.signal_send_chat)
        self.Signals.bind_thickness_change_signal(self.get_setting_change_handler('Thickness'))
        self.Signals.bind_color_change_signal(self.get_setting_change_handler('Color'))
        self.Signals.bind_eraser_change_signal(self.get_setting_change_handler('Eraser'))
        self.Signals.bind_clear_signal(self.get_setting_change_handler('Clear'))

        self.Signals.bind_game_begin_signal(self.get_send_cmd_handler(**make_begin_game_command()))


    def set_gamer_name_id(self, gid=0, gname=''):
        self.GamerId = gid
        self.GamerUsrName = gname

        if self.GamerId == 0:
            self.Panel.GameBeginBtn.setVisible(True)


    # 画板上鼠标移动时画点的对应槽函数
    # 将点添加到buffer，检查buffer容量并发送buffer内所有点
    def signal_paint_point(self, point):
        self.append_point(point)
        if len(self.PointBuffer) == config.client.PointBufferSize:
            self.immediate_send_all_points()


    # 画板上鼠标点击时画点的对应槽函数
    # 将会立刻发送点，会改变画板的状态为painting
    def signal_click_point(self, point):
        x = point.x()
        y = point.y()
        # self.send_cmd(command='ClickPoint', X=x, Y=y)
        self.send_cmd(**make_click_point_command(x, y))


    # 画板上鼠标松开的槽函数
    # 立刻发送所有点
    def signal_release_point(self):
        time.sleep(0.2)
        self.immediate_send_all_points()


    # 返回获得发送指令的处理函数
    def get_send_cmd_handler(self, command, **kwargs):
        def sender():
            self.send_cmd(command=command, **kwargs)
        return sender


    # 获取设置变化的处理函数
    # 实质是闭包封装了一个发送设置变化的函数
    def get_setting_change_handler(self, name):
        def sender(val=None):
            d = {name:val}
            # self.send_cmd(command='SettingChanged', **d)
            self.send_cmd(**make_setting_changed_command(d))
        return sender


    def signal_send_chat(self, msg):
        chat_cmd = make_chat_command(id_=self.GamerId,
                                     name=self.GamerUsrName,
                                     content=msg)
        self.send_cmd(**chat_cmd)
        # self.send_cmd(command='Chat',
        #               id=self.GamerId,
        #               name=self.GamerUsrName,
        #               content=msg)


    # 立刻发送所有点，清空buffer
    def immediate_send_all_points(self):
        self.BufferLock.acquire(True)
        points = []
        for x, y in self.PointBuffer:
            points.append((x,y))
            # points[str(i)] = str(x_) + ' ' + str(y_)
        # send_cmd(self.Socket, 'PaintPoint', points=points)
        send_cmd(self.Socket, **make_paint_point_command(points))
        self.PointBuffer.clear()
        self.BufferLock.release()


    # 添加点到缓冲区
    # 会使用锁保证缓冲区互斥
    def append_point(self, point):
        x = point.x()
        y = point.y()
        self.BufferLock.acquire(True)
        self.PointBuffer.append([x,y])
        self.BufferLock.release()


    def add_gamer(self, gamer_name):
        self.Panel.add_gamer(gamer_name)


    def add_chat_message(self, name, msg):
        self.Panel.add_chat_message(name, msg)


    def update_gamers(self, gamers):
        self.Panel.update_gamers(gamers)


    def update_inform(self, inform):
        self.Panel.update_inform(inform)



    def recv_cmd(self):
        ret = recv_cmd(self.Socket)
        logger.debug('client.engine',
                     'recv cmd: {}'.format(ret))
        return ret


    def send_cmd(self, command, **kwargs):
        logger.debug('client.engine',
                     'send cmd: {}, {}'.format(command, kwargs))
        send_cmd(self.Socket, command, **kwargs)


    def show(self):
        self.Panel.show()









