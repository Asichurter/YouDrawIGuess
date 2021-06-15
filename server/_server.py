import socket
import threading

# from config import DefaultConfigSet, ConnectionConfig
from account import load_account
import time
from queue import Queue

import config
from com.talk import recv_cmd, send_cmd, decode_msg, encode_msg
from log import GlobalLogger as logger
from server.gamer import Gamer

class Server:
    def __init__(self):
        self.MaxCont = config.game.MaxGamer
        self.Account = load_account(config.server.UsrAccountAddr)

        assert self.Account is not None, \
            '用户账户文件损坏！检查config中的路径是否正确或者账户文件是否损坏！'

        # 创建套接字
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置服务器使用固定地址
        self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定端口
        self.Socket.bind(('', config.connect.ServerPort))

        self.Gamers = []
        self.GamerLock = threading.Lock()

        self.CntedUsrNumber = 0
        self.UsrSocket = []
        self.UsrAddr = []
        self.UsrName = []
        self.UsrPoint = []
        self.UsrThread = []
        self.TimerId = {}
        self.TimerThread = {}

        self.Answer = None
        self.Hint = None
        self.PointPool = []
        self.AnsweredGamer = []

        self.CmdQueue = Queue()
    

    def add_gamer(self, socket_obj, addr, user_name):
        self.GamerLock.acquire()

        Id = len(self.Gamers)
        gamer = Gamer(Id, user_name, addr, socket_obj)
        self.Gamers.append(gamer)

        self.GamerLock.release()


    def recv_cmd(self, i, decode=True):
        return recv_cmd(self.UsrSocket[i], decode)


    def send_cmd(self, i, command, **kwargs):
        logger.debug('server.send_cmd',
                     'send cmd: {}, vals: {}'
                     .format(command, kwargs))
        send_cmd(self.UsrSocket[i], command, **kwargs)


    def send_all_cmd(self, command, **kwargs):
        for s_ in self.UsrSocket:
            send_cmd(s_, command, **kwargs)


    def run(self):
        # self.startTimer(0)
        print('Server start !')
        self.login_state()

        for i in range(self.CntedUsrNumber):
            t = threading.Thread(target=self.game_thread, args=(i,), daemon=True)
            self.UsrThread.append(t)

        for t in self.UsrThread:
            t.start()

        self.game_state_()

    def initGameState(self):
        self.fillPointPool()
        self.AnsweredGamer.clear()

    def game_state_(self):
        print('entering game state')
        for cur_gamer_index in range(self.CntedUsrNumber):
            # 每开始一轮游戏，先调用初始化方法
            self.initGameState()

            # 向所有玩家发出新一轮游戏的指令来初始化
            self.send_all_cmd(command='NewRound')

            # 将画图者添加到已完成玩家列表中，防止其自己猜自己
            self.AnsweredGamer.append(cur_gamer_index)

            # 发送游戏提示
            for i,s_ in enumerate(self.UsrSocket):
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
                msg = self.CmdQueue.get()     # 阻塞队列，处理接受到的命令
                cmd, vals = decode_msg(msg)
                if cmd != '':
                    logger.info('server.game',
                                'cmd: {}, vals: {}'.format(cmd, vals))

                if cmd == 'BeginPaint':
                    self.Answer = vals['answer']
                    self.Hint = vals['hint']
                    # 启动倒计时定时器
                    self.\
                        startTimer(timerId=0, downCount=int(config.game.RoundTime), interval=1)
                    print('timer starting!')

                elif cmd == 'Chat':
                    usr_id = int(vals['id'])
                    content = vals['content']

                    if usr_id not in self.AnsweredGamer and self.checkAnswer(content):
                        # 一旦玩家的答案正确
                        print('用户%d的答案%s正确'%(usr_id, content))

                        self.AnsweredGamer.append(usr_id)
                        self.gamerScore(hid=cur_gamer_index, uid=usr_id)
                        self.sendGamerInfo()
                        self.send_all_cmd(command='Chat',
                                          Name='服务器',
                                          Content='%s 已经猜对了答案'%self.UsrName[usr_id])
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
                    for i_,s_ in enumerate(self.UsrSocket):
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

    def game_thread(self, i):
        print('thread starting!')
        self.UsrSocket[i].settimeout(None)
        while True:
            msg = self.recv_cmd(i, False)
            if msg != b'':
                logger.debug('server.game_thread',
                             'receiving msg: {}'.format(msg))
                self.CmdQueue.put(msg)

    def startTimer(self, timerId, downCount=None, interval=1, eps=5e-2):
        def newTimer():
            self.TimerId[timerId] = True
            delta = 1 if downCount is None else -1
            scs = 0 if downCount is None else int(downCount)
            flag = (downCount is None) or (scs > 0)     # 对于倒计时时钟，是否时钟尚存
            print('timer starting: ', timerId)

            while self.TimerId[timerId] and flag:
                time.sleep(interval-eps)

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
                                 'Login指令中缺少 username 和 password 项！')
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
                    self.sendGamerInfo()
                    return

            # 玩家主动或者被动放弃登录
            elif cmd == 'ExitLogin':
                return



    def login_state(self):
        # 欢迎socket监听3秒就开始监听主机命令
        self.Socket.settimeout(config.server.ServerAcceptInterval)
        self.Socket.listen(self.MaxCont)

        login_threads = []

        # 外层循环接受玩家连接
        while True:
            # 接受玩家连接和主机命令
            con_socket, con_addr = self.accept_and_monitor_host()

            # 返回的socket为None，登录状态结束
            if con_socket is None:
                break

            thread = threading.Thread(None,
                                      target=self.login_thread,
                                      args=(con_socket, con_addr))

            login_threads.append(thread)
            thread.start()

        # 等待所有登录
        for thread in login_threads:
            thread.join()

        # 关闭欢迎socket
        self.Socket.close()


    def accept_and_monitor_host(self):
        '''
        使用欢迎套接字来接受玩家连接，同时监听Host的开始游戏命令来终止
        接受更多的玩家连接
        :return: 玩家连接的套接字和地址，如果游戏开始则返回None
        '''
        # 内层循环不断在监听主机命令和监听玩家连接之间循环
        while True:
            try:
                # print('accepting...')\
                con_socket, addr = self.Socket.accept()
                print('new gamer connected...')
                # 接受到新玩家以后，本轮循环不再监听主机命令
                return con_socket, addr
            # 每3秒就切换到监听主机命令
            except socket.timeout:
                if self.CntedUsrNumber != 0:
                    self.UsrSocket[0].settimeout(config.server.HostCommandInterval)
                    try:
                        host_cmd, host_cmd_vals = self.recv_cmd(0, decode=True)

                        # 如果主机发出开始游戏命令，则返回None代表不再接受玩家连接
                        if host_cmd == 'BeginGame':
                            logger.info('server.accept', 'Game has begun!')
                            self.send_all_cmd(command='BeginGame')
                            # for i, s_ in enumerate(self.UsrSocket):
                            #     self.send_cmd(i, command='BeginGame')
                            return None, None
                        else:
                            logger.warning('server.accept',
                                           f'Not accepted command type during login waiting: {host_cmd}, ignore')
                    except socket.timeout:
                        pass

    # def login(self, id):
    #     usr_socket = self.UsrSocket[id]
    #     # 将
    #     usr_socket.settimeout(None)
    #     # 先出于等待登录状态
    #     while True:
    #         cmd, vals = self.recv_cmd(id, decode=True)
    #         # print(cmd, vals)
    #         if cmd == 'Login':
    #             try:
    #                 passed, login_info = self.check_login(vals['Username'], vals['Password'])
    #                 print(passed, login_info)
    #             except KeyError:
    #                 print('Login指令中缺少 username 和 password 项！')
    #                 continue
    #             self.send_cmd(id, command='Login',
    #                               LoginStateCode=1 if passed else 0,
    #                               LoginMessage=login_info,
    #                               ID=id)
    #             # usr_socket.send(login_response)
    #
    #             if passed:
    #                 print('sending gamer info...')
    #                 time.sleep(2)
    #                 self.UsrName.append(vals['Username'])
    #                 self.UsrPoint.append(0)
    #                 self.sendGamerInfo()
    #                 return

    def sendGamerInfo(self):
        gamer_info = self.getGamerInfo()
        self.send_all_cmd(command='GamerInfo', **gamer_info)


    def getGamerInfo(self):
        gamers = []
        for n,p in zip(self.UsrName, self.UsrPoint):
            gamers.append((n,p))
        return {'gamers': gamers}
        # info = 'GamerInfo'
        # for n,p in zip(self.UsrName, self.UsrPoint):
        #     info += '\n{name} {point}'.format(name=n, point=p)
        # return info

    def check_login(self, usr, psw):
        if usr not in self.Account.keys():
            return False, '用户不存在'
        elif usr in self.UsrName:
            return False, '用户已登录'
        elif self.Account[usr] != psw:
            return False, '密码不正确'
        else:
            return True, '登陆成功'

    def checkAnswer(self, answer):
        return self.Answer==answer

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
        self.Socket.close()

if __name__ =='__main__':
    s = Server()
    # p1 = Thread(target=s.run, args=())
    # p1.start()
    # time.sleep(10)
    # print('sending!')
    # s.send_request(0, 'timer', {'id':0})
    #
    # p1.join()
    s.run()

