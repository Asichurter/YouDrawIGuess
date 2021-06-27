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
            handler = get_handler(S_LOGIN_STATE, cmd)
            handler(server, gamer=self, **body)

    def close(self):
        self.Socket.close()

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

    def score(self, s):
        self.Point += s

    def get_info(self):
        return self.UserName, self.Point

class GamerGroup:
    def __init__(self):
        self._GamersLock = Lock()
        self._Gamers = []
        self._GamerIdIndexMapping = {}

    def add_gamer(self, gamer, gamer_id):
        self._GamersLock.acquire()
        self._GamerIdIndexMapping[gamer_id] = len(self._Gamers)
        self._Gamers.append(gamer)
        self._GamersLock.release()

    def get_gamer_by_id(self, id_):
        gamer_index = self._GamerIdIndexMapping.get(id_, None)
        if gamer_index is None:
            logger.error('gamer.GamerGroup',
                         f'No such a index mapping for gamer id {id_}')
            return None
        return self._Gamers[gamer_index]

    def pack_all_gamers_info(self):
        gamers_info = []
        for g in self._Gamers:
            gamers_info.append(g.get_info())
        return gamers_info

    def send_cmd_by_id(self, id_, command, **kwargs):
        gamer = self.get_gamer_by_id(id_)
        gamer.send_cmd(command=command, **kwargs)

    def __iter__(self):
        return iter(self._Gamers)

    def __len__(self):
        return len(self._Gamers)

    def __getitem__(self, idx):
        return self._Gamers[idx]

if __name__ == '__main__':
    gp = GamerGroup()
    gp.add_gamer('a', 0)
    gp.add_gamer('b', 1)
    gp.add_gamer('c', 2)
    gp.add_gamer('d', 3)

    for g in gp:
        print(g)

    print(gp[1])






