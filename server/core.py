import socket
import threading

import time
from queue import Queue

import config
from vals.state import *
from com.talk import recv_cmd, send_cmd, decode_msg, encode_msg
from utils.thread_utils import ThreadValue
from log import GlobalLogger as logger

from server.gamer import Gamer, UnloggedGamer
from server.handlers import get_handler
from server.account import GamerAccount
from vals.command import make_gamer_info_command, CMD_BEGIN_GAME, make_chat_command


class Server:
    def __init__(self):
        self.MaxCont = config.game.MaxGamer
        self.GamerAccount = GamerAccount(config.server.UsrAccountAddr)

        # 创建套接字
        self.WelcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置服务器使用固定地址
        self.WelcomeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定端口
        self.WelcomeSocket.bind(('', config.connect.ServerPort))

        self.UnloggedGamers = []
        self.Gamers = []
        self.GamerLock = threading.Lock()

        # self.GamerCount = 0
        self.UsrSocket = []
        self.UsrAddr = []
        self.UsrName = []
        self.UsrPoint = []
        self.GamerCmdListenThreads = []
        self.TimerId = {}
        self.TimerThread = {}

        self.Answer = None
        self.Hint = None
        self.PointPool = []
        self.AnsweredGamer = []

        self.CmdQueue = Queue()
        self.GameBeginFlag = ThreadValue(True)

    def add_gamer(self, gamer):
        self.GamerLock.acquire()
        self.Gamers.append(gamer)
        self.GamerLock.release()

    def recv_cmd(self, i, decode=True):
        return recv_cmd(self.UsrSocket[i], decode)

    def send_cmd(self, i, command, **kwargs):
        # logger.debug('server.send_cmd',
        #              'send cmd: {}, vals: {}'
        #              .format(command, kwargs))
        self.Gamers[i].send_cmd(command, **kwargs)
        # send_cmd(self.UsrSocket[i], command, **kwargs)

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

    def initGameState(self):
        self.fillPointPool()
        self.AnsweredGamer.clear()

    def game_state(self):
        while True:
            self.send_all_cmd(**make_chat_command(id_=-1,
                                                  name='服务器',
                                                  content='游戏开始的测试信息'))
            time.sleep(2)

    def game_state_(self):
        print('entering game state')
        for cur_gamer_index in range(self.GamerCount):
            # 每开始一轮游戏，先调用初始化方法
            self.initGameState()

            # 向所有玩家发出新一轮游戏的指令来初始化
            self.send_all_cmd(command='NewRound')

            # 将画图者添加到已完成玩家列表中，防止其自己猜自己
            self.AnsweredGamer.append(cur_gamer_index)

            # 发送游戏提示
            for i, s_ in enumerate(self.UsrSocket):
                self.send_cmd(i, command='Inform',
                              Content='现在由 {name} 画图'.format(name=self.UsrName[cur_gamer_index]))

            # time.sleep(1)

            # 向当前画图玩家发出开始画图的指令
            self.send_cmd(cur_gamer_index, command='BeginPaint')

            # # 接受画图玩家出的题
            # cmd, vals = decode_msg(self.recv_cmd(cur_gamer_index))
            # if cmd

            print('thread starting from parent thread!')
            while True:
                msg = self.CmdQueue.get()  # 阻塞队列，处理接受到的命令
                cmd, vals = decode_msg(msg)
                if cmd != '':
                    logger.info('server.game',
                                'cmd: {}, vals: {}'.format(cmd, vals))

                if cmd == 'BeginPaint':
                    self.Answer = vals['answer']
                    self.Hint = vals['hint']
                    # 启动倒计时定时器
                    self. \
                        startTimer(timerId=0, downCount=int(config.game.RoundTime), interval=1)
                    print('timer starting!')

                elif cmd == 'Chat':
                    usr_id = int(vals['id'])
                    content = vals['content']

                    if usr_id not in self.AnsweredGamer and self.checkAnswer(content):
                        # 一旦玩家的答案正确
                        print('用户%d的答案%s正确' % (usr_id, content))

                        self.AnsweredGamer.append(usr_id)
                        self.gamerScore(hid=cur_gamer_index, uid=usr_id)
                        self.send_gamer_info()
                        self.send_all_cmd(command='Chat',
                                          Name='服务器',
                                          Content='%s 已经猜对了答案' % self.UsrName[usr_id])
                        print('游戏进度:', len(self.AnsweredGamer), len(self.UsrPoint))

                        # 如果所有玩家都猜对了
                        if len(self.AnsweredGamer) == len(self.UsrPoint):
                            self.stopTimer(0)
                            # 当前玩家停止画图
                            self.send_cmd(cur_gamer_index, command='StopPaint')
                            # 跳到下一个玩家
                            break

                    # 只有不是正确答案的聊天才会被公布
                    else:
                        self.send_all_cmd(command='Chat', **vals)

                elif cmd == 'Timeout':
                    # for i in range(len(self.UsrSocket)):
                    #     self.send_cmd(i, command='Inform', Content='时间到')
                    self.send_all_cmd(command='Inform', Content='时间到')
                    self.send_cmd(cur_gamer_index, command='StopPaint')
                    time.sleep(2)
                    break

                elif cmd == 'PaintPoint' or \
                        cmd == 'ClickPoint':
                    for i_, s_ in enumerate(self.UsrSocket):
                        if i_ != cur_gamer_index:
                            self.send_cmd(i_, command=cmd, **vals)

                elif cmd == 'TimerEvent':
                    for i_, s_ in enumerate(self.UsrSocket):
                        self.send_cmd(i_, command=cmd, **vals)

                elif cmd == 'SettingChanged':
                    for i_, s_ in enumerate(self.UsrSocket):
                        if i_ != cur_gamer_index:
                            self.send_cmd(i_, command=cmd, **vals)

        self.send_all_cmd(command='EndGame')

    def startTimer(self, timerId, downCount=None, interval=1, eps=5e-2):
        def newTimer():
            self.TimerId[timerId] = True
            delta = 1 if downCount is None else -1
            scs = 0 if downCount is None else int(downCount)
            flag = (downCount is None) or (scs > 0)  # 对于倒计时时钟，是否时钟尚存
            print('timer starting: ', timerId)

            while self.TimerId[timerId] and flag:
                time.sleep(interval - eps)

                # msg = b'TimerEvent\nSecond %d' % scs
                msg, _ = encode_msg(command='TimerEvent',
                                    second=str(scs))
                self.CmdQueue.put(msg)

                flag = (downCount is None) or (scs > 0)
                scs = scs + delta

            # 对于倒计时时钟，时间到的时候会放入一条时间到的指令
            if not flag:
                # msg = b'Timeout'
                msg, _ = encode_msg(command='Timeout')
                self.CmdQueue.put(msg)

            del self.TimerId[timerId]
            del self.TimerThread[timerId]
            print('timer %d exit' % timerId)

        assert timerId not in self.TimerId, '计时器ID已存在！'

        self.TimerThread[timerId] = threading.Thread(target=newTimer, args=(), daemon=True)
        self.TimerThread[timerId].start()

    def stopTimer(self, timerId):
        self.TimerId[timerId] = False
        # 等待0.5秒计时器进程退出
        time.sleep(0.5)

    def login_thread(self, socket_obj, con_addr):
        socket_obj.settimeout(None)
        # 先出于等待登录状态
        while True:
            cmd, vals = recv_cmd(socket_obj, decode=True)
            if cmd == 'Login':
                try:
                    user_name = vals['Username']
                    password = vals['Password']
                    passed, login_info = self.check_login(user_name, password)
                except KeyError:
                    logger.error('server.login',
                                 'Login指令中缺少 username '
                                 '和 password 项！')
                    continue
                send_cmd(socket_obj,
                         command='Login',
                         LoginStateCode=1 if passed else 0,
                         LoginMessage=login_info,
                         ID=id)

                if passed:
                    logger.info('server.login',
                                'sending gamer info...')

                    self.add_gamer(socket_obj, con_addr, user_name)
                    # todo: 修改为Gamer实现
                    self.send_gamer_info()
                    return

            # 玩家主动或者被动放弃登录
            elif cmd == 'ExitLogin':
                return

    def handle_host_begin_game_cmd(self, host_index=0):
        logger.debug('handle_host_cmd',
                     'host handling threading start!')
        while True:
            if len(self.UnloggedGamers) != 0:
                cmd, body = self.UnloggedGamers[host_index].recv_cmd()
                logger.debug('handle_host_cmd',
                             f'cmd: {cmd}, body:{body}')
                handler = get_handler(S_LOGIN, cmd, supress_log=True)
                handler(self, gamer=self.UnloggedGamers[host_index], **body)

                # 该线程如果接收到了主机有关游戏开始的命令后就退出
                if cmd == CMD_BEGIN_GAME:
                    return
            else:
                time.sleep(1)

    def login_state(self):
        # 欢迎socket监听3秒就开始监听主机命令
        self.WelcomeSocket.settimeout(config.server.ServerAcceptInterval)
        self.WelcomeSocket.listen(self.MaxCont)

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

    def send_gamer_info(self):
        gamer_info = self.get_gamer_info()
        self.send_all_cmd(**make_gamer_info_command(gamer_info))

    def get_gamer_info(self):
        gamers = []
        for g in self.Gamers:
            gamers.append((g.UserName, g.Point))
        return gamers

    def checkAnswer(self, answer):
        return self.Answer == answer

    def fillPointPool(self):
        # todo: 计分方式有点问题
        self.PointPool = config.game.GuessPointPool

    def gamerScore(self, hid, uid):
        self.UsrPoint[hid] += config.game.DrawPoint
        self.UsrPoint[uid] += self.PointPool.pop(0)

    def close(self):
        self.send_all_cmd(command='EndGame')
        for s_ in self.UsrSocket:
            s_.close()
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

