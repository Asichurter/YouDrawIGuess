import socket
from config import DefaultConfigSet
from com import decode_msg, encode_msg

addr = ('103.46.128.45', 56509)

class Client:

    def __init__(self, cfgs):
        self.Cfg = cfgs
        # self.GameSignal = True
        # self.GameSignal.clear()

        # 创建套接字
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ClientId = None

    def run(self):
        self.Socket.connect(addr)
        self.game()

    def toggle_game_signal(self):
        self.GameSignal = not self.GameSignal

    def game(self):
        # self.LoginPanel.show()
        # 登录状态，先于服务器取得通讯
        while True:
            # print('waiting for entering usr and psw...')
            # while self.GameSignal:
            #     pass
            print('after waiting...')
            # usrName, password = self.LoginPanel.getUsrAndPsw()
            usrName = input('usrname >> ')
            password = input('password >> ')

            login_command_msg = encode_msg(command='Login', username=usrName, password=password)
            print(login_command_msg)
            self.Socket.send(login_command_msg)
            # 收取服务器的回复
            _, vals = decode_msg(self.Socket.recv(1024))
            login_flag = vals['LoginStateCode']
            login_info = vals['LoginMessage']
            self.ClientId = vals['ID']

            print(login_flag, vals)

            if login_flag == '1':
                break

        # self.LoginPanel.close()

        while True:
            command = input('command >> ')
            command = encode_msg(command=command)
            self.Socket.send(command)

            if command == 'BeginGame':
                break

    def get_login_usr_psw(self):
        pass


        # usr_socket = self.UsrSocket[id]
        # # 先出于等待登录状态
        # while True:
        #     msg = usr_socket.recv(1024)
        #     cmd, vals = decode_msg(msg)
        #     if cmd == 'Login':
        #         try:
        #             passed, login_info = self.checkPermission(vals['username'], vals['password'])
        #         except KeyError:
        #             print('Login指令中缺少 username 和 password 项！')
        #             continue
        #         login_response = encode_msg(command='Login', LoginMessage=login_info)
        #         usr_socket.send(login_response)
        #         if passed:
        #             break

    # def __init__(self, cfgs):
    #     self.Cfg = cfgs
    #
    #     self.Socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # def connect(self):
    #     self.Socket.connect(addr)
    #
    #     p1 = Thread(target=self.send, args=())
    #     p2 = Thread(target=self.receive, args=())
    #     p1.start()
    #     p2.start()
    #     p1.join()
    #     p2.join()
    #
    # def send(self):
    #     print('connect')
    #     while True:
    #         msg = input('>>')
    #         self.Socket.send(msg.encode(encoding='UTF-8'))
    #
    # def receive(self):
    #     while True:
    #         msg = self.Socket.recv(1024)
    #         print(msg)

        #    msg = input('请输入：')
        #     if not msg:
        #         break;
        #     tcpCliSock.send(msg.encode())
        #     data = tcpCliSock.recv(2048)
        #     if not data:
        #         break;
        #     print(data.decode())

if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # g = GamePanel(DefaultConfigSet)
    # l = LoginPanel(g)
    c = Client(DefaultConfigSet)
    # l.setServer(c)
    c.run()

    # t1.join()
    # exit(app.exec_())  # 进入消息循环

