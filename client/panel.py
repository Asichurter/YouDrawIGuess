from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
import time

import config
from client.comp.PaintPanel import PaintPanel
from client.comp.GamerWidget import GamerWidget
from LoginPanel import LoginPanel
from client.signal import ClientSignal


addr = ('103.46.128.45', 36654)
# a = s.HTTPServer()

class GamePanel(widgets.QMainWindow):

    def __init__(self, signals: ClientSignal):
        super(GamePanel, self).__init__()
        self.setWindowTitle('你画我猜')
        # self.GameThread.trigger.connect(self.wait_for_ready)
        self.PointBuffer = []
        # self.PointBufferLock = core.QMutexLocker()
        self.Timer = core.QTimer(self)
        # self.SendTimer.timeout.connect(self.send_and_clear_buffer)
        self.State = None

        self.InputVal = None
        self.Signals = signals

        self.init_ui()
        self.init_slots()


    def init_ui(self):
        # 调整窗口总大小
        self.resize(*config.size.WindowSize)
        self.setFixedSize(*config.size.WindowSize)

        # 全局布局设置
        self.global_layout()

        # 显示玩家信息的组件
        self.init_gamer_layout()

        self.init_message_layout()

        self.setCentralWidget(self.GameWidget)
        print('starting')

        # TODO: 添加玩家信息


    def init_slots(self):
        self.Signals.bind_input_dialog_signal(self.signal_input_dialog)


    # 重置绘图面板
    def reset_paint_panel(self):
        self.PaintPanel.setPenThickness(config.paint.DefaultThickness)
        self.PaintPanel.setPenColor(config.paint.DefaultColor)
        self.PaintPanel.externClear()
        self.PaintPanel.setEraser(False)
        self.PaintPanel.setSettingVisible(False)


    def global_layout(self):
        self.GlobalLayout = widgets.QHBoxLayout()
        self.GamerGlobalLayout = widgets.QGridLayout()
        self.MessageGlobalLayout = widgets.QVBoxLayout()
        self.GlobalLayout.addLayout(self.GamerGlobalLayout)
        self.PaintPanel = PaintPanel(self.Signals, Parent=self)
        self.GlobalLayout.addWidget(self.PaintPanel)
        self.GlobalLayout.addLayout(self.MessageGlobalLayout)

        self.GameWidget = widgets.QWidget()
        self.GameWidget.setLayout(self.GlobalLayout)
        self.setCentralWidget(self.GameWidget)


    def init_message_layout(self):
        self.MsgLayoutLabel = widgets.QLabel('消息')
        self.MessageGlobalLayout.addWidget(self.MsgLayoutLabel,
                                           alignment=core.Qt.AlignHCenter)

        self.MessageWidget = widgets.QTextEdit()
        # self.MessageWidget = widgets.QListWidget()
        self.MessageGlobalLayout.addWidget(self.MessageWidget)

        # 添加输入发送框组件
        self.add_input_dialog()

    def init_gamer_layout(self):
        self.GamerWidgets = [GamerWidget() for i in range(self.Cfg['MaxGamer'])]
        for i,w in enumerate(self.GamerWidgets):
            # print(i,' th widget added')
            self.GamerGlobalLayout.addWidget(w, i, 0)

        self.GameBeginBtn = widgets.QPushButton('开始游戏')
        self.GameBeginBtn.setVisible(False)
        self.GameBeginBtn.clicked.connect(lambda args: self.Signals.GameBeginSignal.emit())
        self.GamerGlobalLayout.addWidget(self.GameBeginBtn, self.Cfg['MaxGamer'], 0)

        self.GamerCount = 0

    def add_input_dialog(self):
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
            self.send_chat_message(msg)
            dialog.clear()

        btn.clicked.connect(send)

        # TODO：不同玩家发送的信息颜色不同设置

    def send_chat_message(self, message):
        '''
            发送消息
        '''
        self.Signals.ChatSendSignal.emit(message)

    def add_message(self, message):
        '''
            向消息框中添加一条信息
        '''
        temp = "<font color='red' size='6'><red>{text}</font>"
        self.MessageWidget.append(temp.format(text=message))

    def add_gamer(self, name):
        '''
            用于初始化界面时，新增玩家
        '''
        if self.GamerCount == self.Cfg['MaxGamer']:
            return False
        else:
            # print(self.GamerCount)
            self.GamerWidgets[self.GamerCount].setName(name)
            self.GamerCount += 1
            return True

    def update_gamer(self, gamers):
        '''
        更新玩家信息
        :param gamers: 玩家名称和分数的字典
        '''
        for i,g in enumerate(gamers.items()):
            # 如果传回的gamer数量比本地gamer数量多，则在本地将这些多的gamer添加
            if i >= self.GamerCount:
                self.add_gamer(g[0])
            else:
                self.GamerWidgets[i].setName(g[0])
                self.GamerWidgets[i].setPoint(g[1])


    # 从对话框中获取输入文本
    def get_input_by_dialog(self, title, label, warning, compulsory=False, textFilter=None, textFilterMsg=None):
        self.InputVal = None
        self.Signal.InputDialogSignal.emit(title,
                                           label,
                                           warning,
                                           compulsory,
                                           textFilter,
                                           textFilterMsg)
        # todo: 测试emit同步/异步？
        # 每1秒钟检查一次是否有输出
        while self.InputVal is None:
            time.sleep(1)
        text = str(self.InputVal)
        # print('text:', text)
        return text


    def closeEvent(self, e):
        # self.SendTimer.stop()
        self.GameThread.exit(0)
        # self.Socket.close()
        exit(0)


    def signal_input_dialog(self, title, label, warning, compulsory=True, textFilter=None, textFilterMsg=''):
        # print('entering get_text_by_dialog...')
        assert not (textFilter is not None and textFilterMsg is None), \
            '设置文本过滤器时，必须给定过滤提示信息'

        while True:
            # print('entering answer...')
            text, okpreessed =  widgets.QInputDialog.getText(self.Panel, title, label,
                                                            widgets.QLineEdit.Normal, "")
            if textFilter is not None and not textFilter(text):
                widgets.QMessageBox.warning(self.Panel,
                                            '非法操作',
                                            textFilterMsg,
                                            widgets.QMessageBox.Yes)
                continue
            if compulsory and (not okpreessed or text == ''):
                widgets.QMessageBox.warning(self.Panel,
                                            '非法操作',
                                            warning,
                                            widgets.QMessageBox.Yes)
                continue
            else:
                # 将从对话框中获取到的值写到一个变量中
                self.InputVal = text
                return


