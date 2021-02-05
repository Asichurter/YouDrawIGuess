from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
import sys
import socket
import time

from config import DefaultConfigSet
from PaintPanel import PaintPanel
from GamerWidget import GamerWidget
from client.comp.LoginPanel import LoginPanel
from com.talk import recv_cmd, send_cmd


addr = ('103.46.128.45', 36654)

# a = s.HTTPServer()

def dummy():
    pass

class GamePanel(widgets.QMainWindow):

    paint_point_signal = core.pyqtSignal(core.QPoint)
    # paint_point_signal = core.pyqtSignal(core.QPoint)
    click_point_signal = core.pyqtSignal(core.QPoint)
    release_point_signal = core.pyqtSignal()
    about_signal = core.pyqtSignal()
    input_dialog_signal = core.pyqtSignal((str, str, str, bool, type(dummy), str))
    thickness_signal = core.pyqtSignal(int)
    color_signal = core.pyqtSignal(str)
    eraser_signal = core.pyqtSignal(bool)
    clear_signal = core.pyqtSignal()
    # input_dialog_signal = core.pyqtSignal()
    # input_dialog_checker = None
    input_val = None

    def __init__(self, cfgs, socket_):
        super(GamePanel, self).__init__()
        self.setWindowTitle('你画我猜')
        self.Cfg = cfgs
        self.Socket = socket_
        # self.GameThread.trigger.connect(self.wait_for_ready)
        self.PointBuffer = []
        # self.PointBufferLock = core.QMutexLocker()
        self.Timer = core.QTimer(self)
        # self.SendTimer.timeout.connect(self.send_and_clear_buffer)
        self.State = None

        self.initUI()

    def initUI(self):
        # 调整窗口总大小
        self.resize(*self.Cfg['WindowSize'])
        self.setFixedSize(*self.Cfg['WindowSize'])

        # 全局布局设置
        self.globalLayout()

        # 显示玩家信息的组件
        self.initGamerLayout()

        self.initMessageLayout()

        self.setCentralWidget(self.GameWidget)
        print('starting')

        # TODO: 添加玩家信息

    def recv_cmd(self):
        '''
        接受来自客户端的命令，利用长度指令，封装了完整命令接受
        的功能，解决了粘包问题
        :return: 收到的完整命令
        '''
        return recv_cmd(self.Socket)
        # cur_length = 0
        # l_msg = b''
        # while :
        #     l_msg += self.Socket.recv(HeaderLength-cur_length)
        #     cur_length = len(l_msg)
        # exp_length = decode_length(l_msg)
        #
        # cur_length = 0
        # msg = b''
        #
        # # 只要接收到的长度还不够，那就继续接受
        # while cur_length < exp_length:
        #     # print('exp length',exp_length,'cur lenth',cur_length)
        #     msg += self.Socket.recv(exp_length-cur_length)
        #     cur_length = len(msg)
        #
        # return msg

    def send_cmd(self, command, **kwargs):
        send_cmd(self.Socket, command, **kwargs)
        # send_msg, l_msg = encode_msg(command=command, **kwargs)
        # self.Socket.send(l_msg)
        # self.Socket.send(send_msg)

    def bind_slots(self):
        self.paint_point_signal.connect(self.send_paint_point)
        self.click_point_signal.connect(self.send_click_point)
        self.release_point_signal.connect(self.send_release_point)
        self.about_signal.connect(self.about)
        self.input_dialog_signal.connect(self.get_input_by_dialog_)
        self.thickness_signal.connect(self.getSettingSender('Thickness'))
        self.color_signal.connect(self.getSettingSender('Color'))
        self.eraser_signal.connect(self.getSettingSender('Eraser'))
        self.clear_signal.connect(self.getSettingSender('Clear'))

        self.PaintPanel.set_paint_point_sender(self.paint_point_signal)
        self.PaintPanel.set_click_point_sender(self.click_point_signal)
        self.PaintPanel.set_release_point_sender(self.release_point_signal)
        self.PaintPanel.setThicknessSender(self.thickness_signal)
        self.PaintPanel.setColorSender(self.color_signal)
        self.PaintPanel.setEraserSender(self.eraser_signal)
        self.PaintPanel.setClearSender(self.clear_signal)

    def activate(self, socket_, id, usrname):
        self.bind_slots()

        self.Socket = socket_
        print('in activate...')
        # self.warn()
        self.ID = int(id)
        self.UsrName = usrname

        # 主机才有开始游戏的按钮
        print('id:', id)
        if self.ID == 0:
            self.GameBeginBtn.setVisible(True)

        _, gamers = decode_msg(self.recv_cmd())
        for g in gamers.keys():
            self.addGamer(g)

        # get_messasge_box(self)
        # self.warn()

        self.GameThread = GameThread(self)
        self.GameThread.start()

        self.show()
        print('showing...')

    def wait_for_ready(self):
        # self.about_signal.emit()
        while True:
            # print('reciving cmd...')
            msg = self.recv_cmd()
            cmd, vals = decode_msg(msg)
            print('new msg', cmd, vals)

            # 指令：更新玩家信息
            if cmd == 'GamerInfo':
                self.updateGamer(vals)

            # 指令：开始游戏
            elif cmd == 'BeginGame':
                print('link start!')
                break

        self.begin()

    def begin(self):
        print('game begining...')
        # self.killTimer(self.timerId)

        while True:
            # 游戏开始
            msg = self.recv_cmd()
            cmd, vals = decode_msg(msg)

            print('cmd',cmd,'vals',vals)

            # 处理聊天信息
            if cmd == 'Chat':
                msg_temp = '{Name}: {Content}'
                self.addMessage(msg_temp.format(**vals))

            # 指令：更新玩家信息
            elif cmd == 'GamerInfo':
                self.updateGamer(vals)

            # 处理通知信息
            elif cmd == 'Inform':
                self.PaintPanel.update_inform(vals['Content'])

            # 接收到可以画画的命令
            elif cmd == 'BeginPaint':
                self.PaintPanel.set_painting(True)
                self.State = 'Painting'
                answer = self.get_input_by_dialog('出题',
                                                  '请输入谜底',
                                                  '谜底不能为空',
                                                  True,
                                                  lambda s: len(s) <= 20,
                                                  '谜底长度不能超过20个字符')
                hint = self.get_input_by_dialog('出题',
                                                '请输入提示',
                                                '',
                                                False,
                                                lambda s: len(s) <= 20,
                                                '提示长度不能超过20个字符')
                print('谜底:', answer, '提示:', hint)
                self.send_cmd(command='BeginPaint', Answer=answer, Hint=hint)
                # 只有要画图的人才能看到设置面板
                self.PaintPanel.set_setting_visible(True)

            elif cmd == 'StopPaint':
                self.PaintPanel.set_painting(False)
                # self.PaintPanel.externClear()
                self.State = 'Waiting'

            # 接收到可以画画的命令
            elif cmd == 'PaintPoint':
                print('print point:', vals)
                xs, ys = [], []
                # 对所有收到的点都画一遍
                for i,p in vals.items():
                    if i == '':
                        continue
                    x, y = p.split(' ')
                    xs.append(int(x))
                    ys.append(int(y))
                self.PaintPanel.extern_paint(x=xs,
                                             y=ys)

            elif cmd == 'ClickPoint':
                self.PaintPanel.extern_click(x=int(vals['X']),
                                             y=int(vals['Y']))

            elif cmd == 'TimerEvent':
                self.PaintPanel.set_clock_digit(vals['Second'])


            elif cmd == 'EndGame':
                self.close()

            elif cmd == 'SettingChanged':
                for k,v in vals.items():
                    if k == 'Color':
                        self.PaintPanel.set_pen_color(v)
                    elif k == 'Thickness':
                        self.PaintPanel.set_pen_thickness(v)
                    elif k == 'Eraser':
                        self.PaintPanel.set_eraser(v)
                    elif k == 'Clear':
                        self.PaintPanel.extern_clear()

            elif cmd == 'NewRound':
                self.resetPaintPanel()

    def resetPaintPanel(self):
        self.PaintPanel.set_pen_thickness(self.Cfg['DefaultThickness'])
        self.PaintPanel.set_pen_color(self.Cfg['DefaultColor'])
        self.PaintPanel.extern_clear()
        self.PaintPanel.set_eraser(False)
        self.PaintPanel.set_setting_visible(False)


    def send_click_point(self, point):
        x = point.x()
        y = point.y()
        self.send_cmd(command='ClickPoint', X=x, Y=y)

    def immediate_send_all_points(self):
        points = {}
        for i, (x_, y_) in enumerate(self.PointBuffer):
            points[str(i)] = str(x_) + ' ' + str(y_)
        self.send_cmd(command='PaintPoint', **points)
        self.PointBuffer.clear()

    def send_release_point(self):
        time.sleep(0.2)
        self.immediate_send_all_points()

    def send_paint_point(self, point):
        x = point.x()
        y = point.y()
        self.PointBuffer.append([x,y])
        if len(self.PointBuffer) == self.Cfg['PointBufferSize']:
            self.immediate_send_all_points()

    def globalLayout(self):
        self.GlobalLayout = widgets.QHBoxLayout()
        self.GamerGlobalLayout = widgets.QGridLayout()
        self.MessageGlobalLayout = widgets.QVBoxLayout()
        self.GlobalLayout.addLayout(self.GamerGlobalLayout)
        self.PaintPanel = PaintPanel(cfgs=self.Cfg, Parent=self)
        self.GlobalLayout.addWidget(self.PaintPanel)
        self.GlobalLayout.addLayout(self.MessageGlobalLayout)

        self.GameWidget = widgets.QWidget()
        self.GameWidget.setLayout(self.GlobalLayout)
        self.setCentralWidget(self.GameWidget)

    def initMessageLayout(self):
        self.MsgLayoutLabel = widgets.QLabel('消息')
        self.MessageGlobalLayout.addWidget(self.MsgLayoutLabel,
                                           alignment=core.Qt.AlignHCenter)

        self.MessageWidget = widgets.QTextEdit()
        # self.MessageWidget = widgets.QListWidget()
        self.MessageGlobalLayout.addWidget(self.MessageWidget)

        # 添加输入发送框组件
        self.addInputDialog()

    def initGamerLayout(self):
        self.GamerWidgets = [GamerWidget() for i in range(self.Cfg['MaxGamer'])]
        for i,w in enumerate(self.GamerWidgets):
            # print(i,' th widget added')
            self.GamerGlobalLayout.addWidget(w, i, 0)

        self.GameBeginBtn = widgets.QPushButton('开始游戏')
        self.GameBeginBtn.setVisible(False)
        self.GameBeginBtn.clicked.connect(self.send_begin_game_cmd)
        self.GamerGlobalLayout.addWidget(self.GameBeginBtn, self.Cfg['MaxGamer'], 0)

        self.GamerCount = 0

    def addInputDialog(self):
        self.InputWidget = widgets.QWidget()
        inLayout = widgets.QHBoxLayout()

        dialog = widgets.QLineEdit(self.InputWidget)
        btn = widgets.QPushButton('发送')     # 发送猜测信息的按钮

        inLayout.addWidget(dialog)
        inLayout.addWidget(btn)
        self.InputWidget.setLayout(inLayout)

        self.MessageGlobalLayout.addWidget(self.InputWidget, alignment=core.Qt.AlignBottom)

        def send():
            msg = dialog.text()
            print(msg)
            self.sendMessage(msg)
            dialog.clear()

        btn.clicked.connect(send)

        # TODO：不同玩家发送的信息颜色不同设置

    def sendMessage(self, message):
        '''
            发送消息
        '''

        # TODO: 添加向服务器发送和接受的代码
        self.send_cmd(command='Chat',
                      ID=self.ID,
                      Name=self.UsrName,
                      Content=message)

    def addMessage(self, message):
        '''
            向消息框中添加一条信息
        '''
        temp = "<font color='red' size='6'><red>{text}</font>"
        self.MessageWidget.append(temp.format(text=message))

    def updateMessage(self):
        for m,w in zip(self.MsgQueue, self.MsgWidget):
            w.setText(m)

    def addGamer(self, name):
        '''
            用于初始化界面时，新增玩家
        '''
        if self.GamerCount == self.Cfg['MaxGamer']:
            return False
        else:
            # print(self.GamerCount)
            self.GamerWidgets[self.GamerCount].set_name(name)
            self.GamerCount += 1
            return True

    def updateGamer(self, gamers):
        '''
        更新玩家信息
        :param gamers: 玩家名称和分数的字典
        '''
        for i,g in enumerate(gamers.items()):
            # 如果传回的gamer数量比本地gamer数量多，则在本地将这些多的gamer添加
            if i >= self.GamerCount:
                self.addGamer(g[0])
            else:
                self.GamerWidgets[i].set_name(g[0])
                self.GamerWidgets[i].set_point(g[1])

    def get_input_by_dialog(self, title, label, warning, compulsory=False, textFilter=None, textFilterMsg=None):
        self.input_val = None
        self.input_dialog_signal.emit(title,
                                      label,
                                      warning,
                                      compulsory,
                                      textFilter,
                                      textFilterMsg)
        # 每1秒钟检查一次是否有输出
        while self.input_val is None:
            time.sleep(1)
        text = str(self.input_val)
        print('text:', text)
        return text

    def send_begin_game_cmd(self):
        self.send_cmd(command='BeginGame')


    def make_send_command_slot_func(self, command, **args):
        def send_msg():
            # self.about()
            print('sending cmd:', command, args)
            self.send_cmd(command=command, **args)

        return send_msg

    def closeEvent(self, e):
        # self.SendTimer.stop()
        self.GameThread.exit(0)
        # self.Socket.close()
        exit(0)

    def get_input_by_dialog_(self, title, label, warning, compulsory=True, textFilter=None, textFilterMsg=''):
        # print('entering get_text_by_dialog...')
        assert not (textFilter is not None and textFilterMsg is None), \
            '设置文本过滤器时，必须给定过滤提示信息'

        while True:
            # print('entering answer...')
            text, okpreessed =  widgets.QInputDialog.getText(self, title, label,
                                                            widgets.QLineEdit.Normal, "")
            if textFilter is not None and not textFilter(text):
                widgets.QMessageBox.warning(self,
                                            '非法操作',
                                            textFilterMsg,
                                            widgets.QMessageBox.Yes)
                continue
            if compulsory and (not okpreessed or text == ''):
                widgets.QMessageBox.warning(self,
                                            '非法操作',
                                            warning,
                                            widgets.QMessageBox.Yes)
            else:
                self.input_val = text
                return

    def getSettingSender(self, name):
        def sender(val=None):
            d = {name:val}
            self.send_cmd(command='SettingChanged', **d)

        return sender

    def warn(self):
        try:
            widgets.QMessageBox.warning(self.GameWidget,
                                        '非法操作',
                                        'warning',
                                        widgets.QMessageBox.Yes)
        except object as e:
            print('error',e)
            exit(0)

    def about(self):
        #QMessageBox.about(self,'关于','这是一个关于消息对话框!')
        # msgBox = widgets.QMessageBox(widgets.QMessageBox.NoIcon, '关于','不要意淫了，早点洗洗睡吧!')
        # # msgBox.setIconPixmap(QPixmap("beauty.png"))
        # msgBox.exec()
        widgets.QMessageBox.warning(self, '测试', '这是一个测试消息框')
        print('returning from about...')

    def get_input(self):
        print('entering get_input...')
        text, ok = widgets.QInputDialog.getText(self, '标题', '内容', widgets.QLineEdit.Normal, "")
        self.input_val = text

    # def timerEvent(self, event):
    #     print('timer event!')
    #     if event.timerId() == self.timerId:
    #         self.PaintPanel.setClockDigit(time.time()%99)

def get_messasge_box(parent):
    widgets.QMessageBox.warning(
                                title='测试',
                                text='测试用消息框',
                                buttons=widgets.QMessageBox.Yes)



class GameThread(core.QThread):
    trigger = core.pyqtSignal()

    def __init__(self, panel, **kwargs):
        super(GameThread, self).__init__(**kwargs)
        self.Panel = panel

    def run(self):
        # self.Panel.timerId = self.Panel.startTimer(1000)
        self.Panel.wait_for_ready()


if __name__ == '__main__':
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(addr)
    print('connecting...')

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)
    # get_messasge_box(None)
    game = GamePanel(DefaultConfigSet, socket_=socket_)
    login = LoginPanel(socket_, cfgs=DefaultConfigSet, activator=game.activate)

    exit(app.exec_())  # 进入消息循环


