from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui
from PyQt5.QtWidgets import QApplication
import sys
import socket

from utils import get_font_stylesheet
from com.talk import send_cmd, recv_cmd

size = (240, 160)
addr = ('103.46.128.45', 36654)

class LoginPanel(widgets.QMainWindow):
    def __init__(self, socket_obj, activator=None):
        super(LoginPanel, self).__init__()

        self.Socket = socket_obj
        self.Activator = activator

        self.setWindowTitle('登录')
        self.resize(*size)
        self.setFixedSize(*size)

        self.Widget = widgets.QWidget()
        self.MainLayout = widgets.QVBoxLayout()
        self.MainLayout.setAlignment(core.Qt.AlignHCenter)

        self.Label = widgets.QLabel('你画我猜 登录')
        self.Label.setStyleSheet(get_font_stylesheet(size=25))
        self.MainLayout.addWidget(self.Label, alignment=core.Qt.AlignTop | core.Qt.AlignHCenter)

        self.FormLayout = widgets.QFormLayout()
        self.UsrName = widgets.QLineEdit()
        self.Psw = widgets.QLineEdit()
        self.Psw.setEchoMode(widgets.QLineEdit.Password)
        self.FormLayout.addRow('用户名', self.UsrName)
        self.FormLayout.addRow('密码', self.Psw)
        self.MainLayout.addLayout(self.FormLayout)

        self.OkButton = widgets.QPushButton('确定')
        self.OkButton.setFixedSize(80, 30)
        self.MainLayout.addWidget(self.OkButton, alignment=core.Qt.AlignHCenter)

        self.Widget.setLayout(self.MainLayout)
        self.setCentralWidget(self.Widget)

        # self.Timer = core.QTimer(self)

        self.initLogic()

        self.show()

    def recv_cmd(self):
        ret = recv_cmd(self.Socket, decode=True)
        print('[Login] recv_cmd: {}'.format(ret))
        return ret


    def send_cmd(self, command, **kwargs):
        send_cmd(self.Socket, command, **kwargs)


    def login(self):
        try:
            usrName, password = self.getUsrAndPsw()

            print('[Login] username: {}, psw: {}'.format(usrName, password))
            self.send_cmd(command='Login', Username=usrName, Password=password)
            # 收取服务器的回复
            _, vals = self.recv_cmd()
            print('[Login] received cmd: {}, args: {}'.format(_, vals))
            login_flag = vals['LoginStateCode']
            login_info = vals['LoginMessage']
            self.ClientId = vals['ID']

            print(login_flag, vals)

            if login_flag == 1:
                self.close()
                print('activating...')
                self.Activator(self.Socket, self.ClientId, self.UsrName.text())
            else:
                widgets.QMessageBox.warning(self,
                                            '登陆失败',
                                            login_info)
                self.UsrName.clear()
                self.Psw.clear()
        except Exception as e:
            print('$ Exception [Login] err: {}'.format(e))
            raise e

        # while True:
        #     command = input('command >> ')
        #     flag = (command == 'BeginGame')
        #     command = encode_msg(command=command)
        #     self.Socket.send(command)
        #
        #     if flag:
        #         break

    def getUsrAndPsw(self):
        usr = self.UsrName.text()
        psw = self.Psw.text()
        return usr, psw

    def initLogic(self):
        self.OkButton.clicked.connect(self.login)

if __name__ == '__main__':
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(addr)
    print('connecting...')

    app = QApplication(sys.argv)
    c = LoginPanel(socket_)

    exit(app.exec_())  # 进入消息循环