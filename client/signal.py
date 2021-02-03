from PyQt5 import QtCore as core

def dummy():
    pass

class ClientSignal:

    def __init__(self):
        self.PaintPointSignal = core.pyqtSignal(core.QPoint)
        self.ClickPointSignal = core.pyqtSignal(core.QPoint)
        self.ReleasePointSignal = core.pyqtSignal()
        self.AboutSignal = core.pyqtSignal()
        self.InputDialogSignal = core.pyqtSignal((str, str, str, bool, type(dummy), str))
        self.ThicknessChangeSignal = core.pyqtSignal(int)
        self.ColorChangeSignal = core.pyqtSignal(str)
        self.EraserChangeSignal = core.pyqtSignal(bool)
        self.ClearSignal = core.pyqtSignal()
        # 发送聊天框内容
        self.ChatSendSignal = core.pyqtSignal(str)
        # 游戏开始信号
        self.GameBeginSignal = core.pyqtSignal()
        # 游戏退出的回调信号
        self.ExitSignal = core.pyqtSignal()

    def bind_paint_point_signal(self, handler):
        self.PaintPointSignal.connect(handler)

    def bind_click_point_signal(self, handler):
        self.ClickPointSignal.connect(handler)

    def bind_release_point_signal(self, handler):
        self.ReleasePointSignal.connect6(handler)

    def bind_about_signal(self, handler):
        self.AboutSignal.connect(handler)

    def bind_input_dialog_signal(self, handler):
        self.InputDialogSignal.connect(handler)

    def bind_thickness_change_signal(self, handler):
        self.ThicknessChangeSignal.connect(handler)

    def bind_color_change_signal(self, handler):
        self.ColorChangeSignal.connect(handler)

    def bind_eraser_change_signal(self, handler):
        self.EraserChangeSignal.connect(handler)

    def bind_clear_signal(self, handler):
        self.ClearSignal.connect(handler)

    def bind_chat_send_signal(self, handler):
        self.ChatSendSignal.connect(handler)

    def bind_game_begin_signal(self, handler):
        self.GameBeginSignal.connect(handler)

    def bind_exit_signal(self, handler):
        self.ExitSignal.connect(handler)
