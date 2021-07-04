import socket
import threading

import time
from queue import Queue

import config

from com.talk import recv_cmd, send_cmd, decode_msg, encode_msg
from utils.thread_utils import ThreadValue
from log import GlobalLogger as logger

from server.gamer import UnloggedGamer, GamerGroup
from server.handlers import get_handler
from server.account import GamerAccount
from server.game import GameLogic
from server.message import ServerMessage
from server.timer.timer_manager import TimerManager
from vals.state import *
from vals.error import ServerHandlingError, DecodeError
from vals.command import *


class Server:
    def __init__(self):

        self.GamerAccount = GamerAccount(config.server.UsrAccountAddr)

        # 创建套接字
        self.WelcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置服务器使用固定地址
        self.WelcomeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定端口
        self.WelcomeSocket.bind(('', config.connect.ServerPort))

        self.MaxGamer = config.game.MaxGamer    # 最大游戏玩家数量
        self.UnloggedGamers = []                # socket已连接，但是逻辑还没有登录的玩家
        self.Gamers = GamerGroup()              # 已登录的玩家群组
        self.GameRoundPerGamer = 1              # 每一个玩家出题的循环次数
        self.ServerMessage = ServerMessage()    # 服务器端发送消息模板类
        self.TimerManager = TimerManager()      # 服务器端计时器管理实例，可以方便地创建定时器
        self.GamerCmdListenThreads = []         # 游戏状态消息循环监听的消息接受线程列表
        self.GameLogic = None                   # 游戏逻辑实体类
        self.CmdQueue = Queue()                 # 监听消息线程间通信队列
        self.GameBeginFlag = ThreadValue(True)  # 指示游戏是否开始的标志
        self.MessageLoopFlag = True             # 指示消息循环是否退出的标志

    def send_cmd_by_id(self, id_, command, **kwargs):
        gamer = self.Gamers.get_gamer_by_id(id_)
        gamer.send_cmd(command=command, **kwargs)

    def send_all_cmd(self, command, **kwargs):
        for g in self.Gamers:
            g.send_cmd(command, **kwargs)

    def send_all_cmd_unlogged(self, command, **kwargs):
        for g in self.UnloggedGamers:
            g.send_cmd(command, **kwargs)

    def run(self):
        self.login_state()

        # 对所有gamer，启动监听其请求的线程
        for g in self.Gamers:
            t = threading.Thread(target=g.listen_gamer_command, args=(self.CmdQueue,), daemon=True)
            self.GamerCmdListenThreads.append(t)

        for t in self.GamerCmdListenThreads:
            t.start()

        self.game_state()

    def game_state(self):
        logger.debug('server.gamer_state',
                     'entering game state')
        # 初始化游戏逻辑
        self.GameLogic = GameLogic(len(self.Gamers))

        for round_index in range(self.GameRoundPerGamer):
            # 游戏循环次数等于玩家数量
            for cur_gamer_index in range(len(self.Gamers)):
                cur_gamer = self.Gamers[cur_gamer_index]

                self.GameLogic.init_game_state(cur_gamer.Id)
                self.send_all_cmd(**make_newround_command())
                # 将当前出题者加入到已回答玩家列表中，防止其自己猜自己
                self.GameLogic.add_answered_gamer_id(cur_gamer.Id)
                # 发送开始画图和通告画图者的通知
                paint_message = self.ServerMessage.make_paint_inform_message(cur_gamer.UserName)
                self.send_all_cmd(**make_inform_command(paint_message))
                # 当前画图者发出开始画图指令
                cur_gamer.send_cmd(**make_begin_paint_command())

                # 进入指令处理循环
                self.MessageLoopFlag = True
                while self.MessageLoopFlag:
                    msg = self.CmdQueue.get()  # 阻塞队列，处理接受到的命令
                    try:
                        cmd, cmd_body = decode_msg(msg, raise_exception=True)
                        handler = get_handler(S_GAME_STATE, cmd)
                        handler(self,
                                cur_gamer=cur_gamer,
                                raw_message=msg,
                                **cmd_body)
                    except DecodeError as de:
                        logger.error('server.game_state',
                                     f'decoding error in game message loop: {de}')
                    except Exception as e:
                        she = ServerHandlingError(cmd, cmd_body, e)
                        logger.error('server.game_state',
                                     f'unknown error when handling in game state: {she}')

        # 关闭游戏
        self.close()

    def handle_host_begin_game_cmd(self, host_index=0):
        logger.debug('handle_host_cmd',
                     'host handling threading start!')
        while True:
            if len(self.UnloggedGamers) != 0:
                cmd, body = self.UnloggedGamers[host_index].recv_cmd()
                logger.debug('handle_host_cmd',
                             f'cmd: {cmd}, body:{body}')
                handler = get_handler(S_LOGIN_STATE, cmd, supress_log=True)
                handler(self, gamer=self.UnloggedGamers[host_index], **body)

                # 该线程如果接收到了主机有关游戏开始的命令后就退出
                if cmd == CMD_BEGIN_GAME:
                    return
            else:
                time.sleep(1)

    def login_state(self):
        # 欢迎socket监听3秒就开始监听主机命令
        self.WelcomeSocket.settimeout(config.server.ServerAcceptInterval)
        self.WelcomeSocket.listen(self.MaxGamer)

        login_threads = []
        # 外层循环接受玩家连接
        while True:
            # 接受玩家连接的套接字
            gamer = self.accept_new_gamer()
            if gamer is None:       # accept内部逻辑会判断是否停止接受更多玩家，以None返回
                break

            # 每一个连接的套接字都启用一个线程处理登录
            login_thread = threading.Thread(None,
                                      target=gamer.check_login,
                                      args=(self,))
            login_thread.start()

            # 主机线程处理
            if len(self.UnloggedGamers) == 1:
                # 必须等到主机登录线程结束以后再启动主机的监听线程
                # 同时，主机没有登录成功时，阻塞其他玩家的登录
                login_thread.join()
                host_thread = threading.Thread(None,
                                               target=self.handle_host_begin_game_cmd,
                                               args=(0,))
                login_threads.append(host_thread)
                host_thread.start()
            else:
                login_threads.append(login_thread)

        # 等待所有玩家登录就绪
        # todo: 玩家登录目前没有超时检查
        for login_thread in login_threads:
            login_thread.join()

        # 关闭欢迎socket
        self.WelcomeSocket.close()

    def accept_new_gamer(self):
        '''
        使用欢迎套接字来接受玩家连接，同时监听Host的开始游戏命令来终止
        接受更多的玩家连接
        :return: 玩家连接的套接字和地址，如果游戏开始则返回None
        '''
        self.WelcomeSocket.settimeout(config.server.HostCommandInterval)   # 设置accept退出的检查周期
        while self.GameBeginFlag.get_val():
            try:
                con_socket, addr = self.WelcomeSocket.accept()
                logger.info('Server.login', 'new gamer connecting...')
                gamer = UnloggedGamer(len(self.UnloggedGamers), addr, con_socket)
                # 接受到新玩家以后加入到gamer列表中
                # 由于accept套接字的时候是串行的，因此不需要互斥读写未登录玩家列表
                self.UnloggedGamers.append(gamer)
                return gamer
            # socket超时后检查游戏开始的全局flag是否被修改
            except socket.timeout:
                pass
        return None

    def close(self):
        self.send_all_cmd(**make_end_game_command())
        for gamer in self.Gamers:
            gamer.close()
        self.WelcomeSocket.close()


if __name__ == '__main__':
    s = Server()
    # p1 = Thread(target=s.run, args=())
    # p1.start()
    # time.sleep(10)
    # print('sending!')
    # s.send_request(0, 'timer', {'id':0})
    #
    # p1.join()
    s.run()

