from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap, QPainter, QPoint, QPaintEvent, QMouseEvent, QPen, \
    QColor, QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

import time

from client.signal import ClientSignal

board_resolution = (1240, 860)
default_thickness = 6
default_color = 'black'

class PaintBoard(QWidget):

    set_paint = pyqtSignal(bool)

    def __init__(self, signals: ClientSignal, Parent=None):
        '''
        Constructor
        '''
        super().__init__(Parent)

        self.Signals = signals


        # 是否是本玩家在画图
        # 判断是否需要发送画图信息
        self.Painting = False
        self.BoardSize = QSize(*board_resolution)

        # 新建QPixmap作为画板，尺寸为size
        self.Board = QPixmap(self.BoardSize)
        self.Board.fill(Qt.white)  # 用白色填充画板

        self.IsEmpty = True  # 默认为空画板
        self.EraserMode = False  # 默认为禁用橡皮擦模式

        self.LastPos = QPoint(0, 0)  # 上一次鼠标位置
        self.CurrentPos = QPoint(0, 0)  # 当前的鼠标位置

        self.Painter = QPainter()  # 新建绘图工具

        self.Thickness = default_thickness  # 默认画笔粗细为10px
        self.PenColor = QColor(default_color)  # 设置默认画笔颜色为黑色
        self.ColorList = QColor.colorNames()  # 获取颜色列表

        self.set_paint.connect(self.set_painting)
        self.PaintPoints = []


        self.init_view()


    def init_view(self):
        # 设置界面的尺寸为size
        self.setFixedSize(self.BoardSize)

    def set_painting(self, painting):
        # print('seting painting to', painting)
        self.Painting = painting


    def set_pen_thickness(self, thickness):
        self.Thickness = int(thickness)


    def set_pen_color(self, color):
        self.PenColor = QColor(color)


    def set_eraser(self, e):
        print('eraser setting changed to', e)
        self.EraserMode = e
        if self.Painting:
            self.Signals.EraserChangeSignal.emit(e)
            # self.EraserSender.emit(e)


    def clear(self):
        if self.Painting:
            self.Signals.ClearSignal.emit()
            # self.ClearSender.emit()
        # 清空画板
        self.Board.fill(Qt.white)
        self.repaint()#update()
        self.IsEmpty = True


    def change_pen_color(self, color="black"):
        print('color changed:', color)
        if self.Painting:
            self.Signals.ColorChangeSignal.emit(color)
            # self.ColorSender.emit(color)
        # 改变画笔颜色
        self.PenColor = QColor(color)

    def change_pen_thickness(self, thickness=default_thickness):
        if self.Painting:
            self.Signals.ThicknessChangeSignal.emit(thickness)
            # self.ThicknessSender.emit(thickness)
        # 改变画笔粗细
        self.Thickness = thickness
        # print('thickness:',type(self.thickness), self.thickness)

    # 返回画板是否为空
    def is_empty(self):
        return self.IsEmpty

    def get_content_as_QImage(self):
        # 获取画板内容（返回QImage）
        image = self.Board.toImage()
        return image


    def paintEvent(self, paintEvent):
        # 绘图事件
        # 绘图时必须使用QPainter的实例，此处为painter
        # 绘图在begin()函数与end()函数间进行
        # begin(param)的参数要指定绘图设备，即把图画在哪里
        # drawPixmap用于绘制QPixmap类型的对象
        self.Painter.begin(self)
        # 0,0为绘图的左上角起点的坐标，board即要绘制的图
        self.Painter.drawPixmap(0, 0, self.Board)
        self.Painter.end()


    def mousePressEvent(self, mouseEvent):
        # 鼠标按下时，获取鼠标的当前位置保存为上一次位置
        self.CurrentPos = mouseEvent.pos()
        self.LastPos = self.CurrentPos

        if self.Painting:
            self.Signals.ClickPointSignal.emit(mouseEvent.pos())
            # self.click_point_sender.emit(mouseEvent.pos())


    def mouseMoveEvent(self, mouseEvent):
        # print('moving! painting=', self.Painting)
        if self.Painting:
            # 鼠标移动时，更新当前位置，并在上一个位置和当前位置间画线
            self.CurrentPos = mouseEvent.pos()
            self.paint_point()
            # print('painting...')
            self.repaint()
            # print('complete painting...')
            self.LastPos = self.CurrentPos

            # self.paint_points.append([self.currentPos.x(), self.currentPos.y()])
            # self.paint_point_sender.emit(mouseEvent.pos())
            self.Signals.PaintPointSignal.emit(mouseEvent.pos())

    def mouseReleaseEvent(self, mouseEvent):
        self.IsEmpty = False  # 画板不再为空
        if self.Painting:
            self.Signals.ReleasePointSignal.emit()
            # self.release_point_sender.emit()
            # self.paint_points.clear()

    def paint_point(self):
        self.Painter.begin(self.Board)

        if not self.EraserMode:
            # 非橡皮擦模式
            self.Painter.setPen(QPen(self.PenColor, self.Thickness))  # 设置画笔颜色，粗细
        else:
            # 橡皮擦模式下画笔为纯白色，粗细为10
            self.Painter.setPen(QPen(Qt.white, 10))
            # 画线

        self.Painter.drawLine(self.LastPos, self.CurrentPos)
        self.Painter.end()


    def extern_click(self, x, y):
        self.LastPos = QPoint(x, y)
        self.CurrentPos = QPoint(x, y)


    def extern_paint(self, ps):
        for x,y in ps:
            self.CurrentPos = QPoint(x, y)
            self.paint_point()
            self.LastPos = self.CurrentPos
        self.repaint()


    def reset_last_point(self, x, y):
        self.LastPos = QPoint(x, y)
        self.CurrentPos = QPoint(x, y)