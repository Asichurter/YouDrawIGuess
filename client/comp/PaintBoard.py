from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap, QPainter, QPoint, QPaintEvent, QMouseEvent, QPen, \
    QColor, QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

import time

board_resolution = (1240, 860)
default_thickness = 6
default_color = 'black'

class PaintBoard(QWidget):

    set_paint = pyqtSignal(bool)

    def __init__(self, signals, Parent=None):
        '''
        Constructor
        '''
        super().__init__(Parent)

        self.Signals = signals
        self.InitData()  # 先初始化数据，再初始化界面
        self.InitView()

    def InitData(self):

        self.Painting = False
        self.size = QSize(*board_resolution)

        # 新建QPixmap作为画板，尺寸为size
        self.board = QPixmap(self.size)
        self.board.fill(Qt.white)  # 用白色填充画板

        self.IsEmpty = True  # 默认为空画板
        self.EraserMode = False  # 默认为禁用橡皮擦模式

        self.lastPos = QPoint(0, 0)  # 上一次鼠标位置
        self.currentPos = QPoint(0, 0)  # 当前的鼠标位置

        self.painter = QPainter()  # 新建绘图工具

        self.thickness = default_thickness  # 默认画笔粗细为10px
        self.penColor = QColor(default_color)  # 设置默认画笔颜色为黑色
        self.colorList = QColor.colorNames()  # 获取颜色列表

        self.set_paint.connect(self.setPainting)
        self.paint_point_sender = None
        self.click_point_sender = None
        self.paint_points = []

    def InitView(self):
        # 设置界面的尺寸为size
        self.setFixedSize(self.size)

    def setPainting(self, painting):
        # print('seting painting to', painting)
        self.Painting = painting

    def set_paint_point_sender(self, sender):
        self.paint_point_sender = sender

    def set_click_point_sender(self, sender):
        self.click_point_sender = sender

    def set_release_point_sender(self, sender):
        self.release_point_sender = sender

    def setColorSender(self, sender):
        self.ColorSender = sender

    def setThicknessSender(self, sender):
        self.ThicknessSender = sender

    def setEraserSender(self, sender):
        self.EraserSender = sender

    def setClearSender(self, sender):
        self.ClearSender = sender

    def setPenThickness(self, thickness):
        # print('thickness changed to', self.thickness)
        self.thickness = int(thickness)
        # print('returning from thickness setting...')

    def setPenColor(self, color):
        self.penColor = QColor(color)

    def setEraser(self, e):
        print('eraser setting changed to', e)
        self.EraserMode = e
        if self.Painting:
            self.EraserSender.emit(e)

    def Clear(self):
        if self.Painting:
            self.ClearSender.emit()
        # 清空画板
        self.board.fill(Qt.white)
        self.repaint()#update()
        self.IsEmpty = True

    def ChangePenColor(self, color="black"):
        print('color changed:', color)
        if self.Painting:
            self.ColorSender.emit(color)
        # 改变画笔颜色
        self.penColor = QColor(color)

    def ChangePenThickness(self, thickness=default_thickness):
        if self.Painting:
            self.ThicknessSender.emit(thickness)
        # 改变画笔粗细
        self.thickness = thickness
        # print('thickness:',type(self.thickness), self.thickness)

    def IsEmpty(self):
        # 返回画板是否为空
        return self.IsEmpty

    def GetContentAsQImage(self):
        # 获取画板内容（返回QImage）
        image = self.board.toImage()
        return image

    def paintEvent(self, paintEvent):
        # 绘图事件
        # 绘图时必须使用QPainter的实例，此处为painter
        # 绘图在begin()函数与end()函数间进行
        # begin(param)的参数要指定绘图设备，即把图画在哪里
        # drawPixmap用于绘制QPixmap类型的对象
        self.painter.begin(self)
        # 0,0为绘图的左上角起点的坐标，board即要绘制的图
        self.painter.drawPixmap(0, 0, self.board)
        self.painter.end()

    def mousePressEvent(self, mouseEvent):
        # 鼠标按下时，获取鼠标的当前位置保存为上一次位置
        self.currentPos = mouseEvent.pos()
        self.lastPos = self.currentPos

        if self.Painting:
            self.click_point_sender.emit(mouseEvent.pos())

    def mouseMoveEvent(self, mouseEvent):
        # print('moving! painting=', self.Painting)
        if self.Painting:
            # 鼠标移动时，更新当前位置，并在上一个位置和当前位置间画线
            self.currentPos = mouseEvent.pos()
            self.paintPoint()
            # print('painting...')
            self.repaint()
            # print('complete painting...')
            self.lastPos = self.currentPos

            # self.paint_points.append([self.currentPos.x(), self.currentPos.y()])
            self.paint_point_sender.emit(mouseEvent.pos())

    def mouseReleaseEvent(self, mouseEvent):
        self.IsEmpty = False  # 画板不再为空
        if self.Painting:
            self.release_point_sender.emit()
            # self.paint_points.clear()

    def paintPoint(self):
        self.painter.begin(self.board)

        if not self.EraserMode:
            # 非橡皮擦模式
            self.painter.setPen(QPen(self.penColor, self.thickness))  # 设置画笔颜色，粗细
        else:
            # 橡皮擦模式下画笔为纯白色，粗细为10
            self.painter.setPen(QPen(Qt.white, 10))
            # 画线

        self.painter.drawLine(self.lastPos, self.currentPos)
        self.painter.end()

    def extern_click(self, x, y):
        self.lastPos = QPoint(x, y)
        self.currentPos = QPoint(x, y)

    def extern_paint(self, xs, ys):
        for x,y in zip(xs, ys):
            self.currentPos = QPoint(x, y)
            self.paintPoint()
            self.lastPos = self.currentPos
        self.repaint()

        # self.currentPos = QPoint(x, y)
        # self.paintPoint(extern=True)
        # self.lastPos = self.currentPos

    def resetLastPoint(self, x, y):
        self.lastPos = QPoint(x, y)
        self.currentPos = QPoint(x, y)