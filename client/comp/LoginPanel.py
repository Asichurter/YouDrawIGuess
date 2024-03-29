from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui
from PyQt5.QtWidgets import QApplication
import sys
import socket
import time

from utils.style_utils import get_qlabel_font_stylesheet
from com.talk import send_cmd, recv_cmd
from log import GlobalLogger as logger
from vals.command import CMD_LOGIN_RESULT, make_login_command, parse_login_result_command
import config

size = (240, 160)

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
        self.Label.setStyleSheet(get_qlabel_font_stylesheet(size=25))
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
        return ret


    def send_cmd(self, command, **kwargs):
        send_cmd(self.Socket, command, **kwargs)


    def login(self):
        try:
            usrName, password = self.getUsrAndPsw()

            logger.info('LoginPanel.login',
                        'username: {}, psw: {}'.format(usrName, password))
            self.send_cmd(**make_login_command(usrName, password))
            # self.send_cmd(command='Login', Username=usrName, Password=password)
            # 收取服务器的回复

            while True:
                cmd, body = self.recv_cmd()
                if cmd == CMD_LOGIN_RESULT:
                    break
                else:
                    logger.warning('LoginPanel.login',
                                   'recv {} cmd with {}, skip'.format(cmd, body))
                    time.sleep(1)

            logger.info('LoginPanel.login',
                        'login success: {}'.format(body))

            # login_status_code = body['LoginStateCode']
            # login_info = body['LoginMessage']
            login_status_code, login_info, ID = parse_login_result_command(body)
            self.ClientId = ID
            if login_status_code == 1:
                self.close()
                logger.info('LoginPanel.login',
                            'activating...')
                self.Activator(self.Socket, self.ClientId, self.UsrName.text())
            else:
                widgets.QMessageBox.warning(self,
                                            '登陆失败',
                                            login_info)
                # self.UsrName.clear()
                self.Psw.clear()
        except Exception as e:
            logger.error('LoginPanel.login','Fail to login, err: {}'.format(e))
            raise e


    def getUsrAndPsw(self):
        usr = self.UsrName.text()
        psw = self.Psw.text()
        return usr, psw

    def initLogic(self):
        self.OkButton.clicked.connect(self.login)