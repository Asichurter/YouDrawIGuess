from threading import Lock

import config
from com.talk import *
from server.handlers import get_handler
from vals.state import *
from utils.thread_utils import ThreadValue
from log import GlobalLogger as logger

class UnloggedGamer:
    def __init__(self, id_, addr, socket_obj):
        self.UnloggedID = id_
        self.Address = addr
        self.Socket = socket_obj
        self.SocketSendLock = Lock()
        self.SocketRcvLock = Lock()
        self.LoginFlag = ThreadValue(False)

    def send_cmd(self, command, **kwargs):
        self.SocketSendLock.acquire()
        send_cmd(self.Socket, command, **kwargs)
        self.SocketSendLock.release()

    def recv_cmd(self, decode=True):
        self.SocketRcvLock.acquire()
        res = recv_cmd(self.Socket, decode=decode)
        self.SocketRcvLock.release()
        return res

    def check_login(self, server):
        self.Socket.settimeout(None)    # 将Socket超时设置为无穷
        while not self.LoginFlag.get_val():
            cmd, body = self.recv_cmd()
            handler = get_handler(S_LOGIN, cmd)
            handler(server, gamer=self, **body)

class Gamer(UnloggedGamer):
    def __init__(self, unlogged_gamer: UnloggedGamer,
                 gamer_id, gamer_name):
        super().__init__(-1, unlogged_gamer.Address, unlogged_gamer.Socket)
        self.Id = gamer_id
        self.UserName = gamer_name
        self.Point = 0

    def listen_gamer_command(self, queue):
        self.Socket.settimeout(None)
        # todo:监听循环退出机制补充
        while True:
            msg = self.recv_cmd(decode=False)
            if msg != b'':
                logger.debug('server.game_thread',
                             'receiving msg: {}'.format(msg))
                queue.put(msg)






