import PyQt5 as qt
from PyQt5.Qt import QWidget, QColor, QPixmap, QIcon, QSize, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QSplitter, \
    QComboBox, QLabel, QSpinBox, QLCDNumber
import PyQt5.QtCore as core
from PaintBoard import PaintBoard, default_thickness, default_color

import config

panel_resolution = (1280, 960)

class PaintPanel(QWidget):

    def __init__(self, signals, Parent=None):
        '''
        Constructor
        '''
        super().__init__(Parent)

        self.InitData(signals)  # 先初始化数据，再初始化界面
        self.InitView()

    def InitData(self, signals):
        '''
                  初始化成员变量
        '''
        self.paintBoard = PaintBoard(signals, Parent=self)
        # 获取颜色列表(字符串类型)
        self.colorList = QColor.colorNames()

    def InitView(self):
        '''
                  初始化界面
        '''
        self.setFixedSize(*panel_resolution)
        self.setWindowTitle("PaintBoard Example PyQt5")

        # 新建一个水平布局作为本窗体的主布局
        main_layout = QVBoxLayout(self)
        # 设置主布局内边距以及控件间距为10px
        main_layout.setSpacing(10)

        # 新建垂直子布局用于放置按键
        sub_layout = QHBoxLayout()
        sub_layout.setContentsMargins(100,0,100,0)

        # 设置此子布局和内部控件的间距为10px
        # sub_layout.setContentsMargins(10, 10, 10, 10)

        # ---------------------通知栏和时钟--------------------------
        self.InformLayout = QHBoxLayout()
        self.InformWidget = QLabel('')
        self.InformLayout.addWidget(self.InformWidget)
        self.InformClock = QLCDNumber(self)
        self.InformClock.setDigitCount(3)
        self.InformClock.setMode(QLCDNumber.Dec)
        self.InformClock.setSegmentStyle(QLCDNumber.Flat)
        self.InformLayout.addWidget(self.InformClock)
        main_layout.addLayout(self.InformLayout)
        # ---------------------------------------------------

        # 在主界面左上侧放置画板
        main_layout.addWidget(self.paintBoard)

        # ---------------------橡皮擦--------------------------
        self.cbtn_Eraser = QCheckBox("使用橡皮擦")
        self.cbtn_Eraser.setParent(self)
        sub_layout.addWidget(self.cbtn_Eraser)
        # ---------------------------------------------------

        # splitter = QSplitter(self)  # 占位符
        # sub_layout.addWidget(splitter)

        # ------------------------笔画粗细-----------------------
        self.pen_thick_child_panel = QHBoxLayout()
        self.label_penThickness = QLabel(self)
        self.label_penThickness.setText("画笔粗细")
        self.label_penThickness.setAlignment(core.Qt.AlignRight | core.Qt.AlignVCenter)
        self.pen_thick_child_panel.addWidget(self.label_penThickness)
        self.spinBox_penThickness = QSpinBox(self)
        self.spinBox_penThickness.setMaximum(20)
        self.spinBox_penThickness.setMinimum(2)
        self.spinBox_penThickness.setValue(config.paint.DefaultThickness)  # 默认粗细为10
        self.spinBox_penThickness.setSingleStep(2)  # 最小变化值为2
        self.pen_thick_child_panel.addWidget(self.spinBox_penThickness)
        sub_layout.addLayout(self.pen_thick_child_panel)
        # ---------------------------------------------------


        # -----------------------笔划颜色-------------------------
        self.pen_color_child_panel = QHBoxLayout()
        self.label_penColor = QLabel(self)
        self.label_penColor.setAlignment(core.Qt.AlignRight | core.Qt.AlignVCenter)
        self.label_penColor.setText("画笔颜色")
        self.pen_color_child_panel.addWidget(self.label_penColor)
        self.comboBox_penColor = QComboBox(self)
        self.fillColorList(self.comboBox_penColor, self.colorList, default_color)  # 用各种颜色填充下拉列表
        # ---------------------------------------------------


        # -------------------------清空画板按钮----------------------
        self.pen_color_child_panel.addWidget(self.comboBox_penColor)
        sub_layout.addLayout(self.pen_color_child_panel)
        self.ctrl_child_panel = QHBoxLayout()
        self.btn_Clear = QPushButton("清空画板")
        self.btn_Clear.setParent(self)  # 设置父对象为本界面
        self.ctrl_child_panel.addWidget(self.btn_Clear)
        sub_layout.addLayout(self.ctrl_child_panel)
        # ---------------------------------------------------


        # -----------------------退出按钮-----------------------
        # self.btn_Quit = QPushButton("退出")
        # self.btn_Quit.setParent(self)  # 设置父对象为本界面
        # self.ctrl_child_panel.addWidget(self.btn_Quit)
        # ---------------------------------------------------

        self.InitLogic()

        main_layout.addLayout(sub_layout)  # 将子布局加入主布局

    def InitLogic(self):
        '''
            初始化所有组件的事件处理逻辑
        '''
        # 橡皮擦点击事件处理
        self.cbtn_Eraser.clicked.connect(self.on_cbtn_Eraser_clicked)

        # 笔划粗细改变事件处理
        self.spinBox_penThickness.valueChanged.connect(
            self.on_PenThicknessChange)  # 关联spinBox值变化信号和函数on_PenThicknessChange

        # 笔划颜色改变事件处理
        self.comboBox_penColor.currentIndexChanged.connect(
            self.on_PenColorChange)  # 关联下拉列表的当前索引变更信号与函数on_PenColorChange

        # 清空画板按钮事件处理
        self.btn_Clear.clicked.connect(self.paintBoard.Clear)

        # 退出事件处理
        # self.btn_Quit.clicked.connect(self.Quit)

    def update_inform(self, inform):
        self.InformWidget.setText(inform)

    def fillColorList(self, comboBox, valList, defVal):
        '''
            填充下拉菜单中的菜单项，使用colorList填充
        '''
        index_default = self.colorList.index(config.paint.DefaultColor)
        index = 0
        for color in valList:
            if color == defVal:
                index_default = index
            index += 1
            pix = QPixmap(70, 20)
            pix.fill(QColor(color))
            comboBox.addItem(QIcon(pix), None)
            comboBox.setIconSize(QSize(70, 20))
            comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        assert default_color != -1, '默认颜色在颜色列表中不存在！'
        comboBox.setCurrentIndex(index_default)

    def setPainting(self, painting):
        self.paintBoard.set_paint.emit(painting)

    def set_paint_point_sender(self, sender):
        self.paintBoard.set_paint_point_sender(sender)

    def set_click_point_sender(self, sender):
        self.paintBoard.set_click_point_sender(sender)

    def set_release_point_sender(self, sender):
        self.paintBoard.set_release_point_sender(sender)

    def setThicknessSender(self, sender):
        self.paintBoard.setThicknessSender(sender)

    def setColorSender(self, sender):
        self.paintBoard.setColorSender(sender)

    def setEraserSender(self, sender):
        self.paintBoard.setEraserSender(sender)

    def setClearSender(self, sender):
        self.paintBoard.setClearSender(sender)

    def setClockDigit(self, number):
        self.InformClock.display(str(number))

    def setPenColor(self, color):
        self.paintBoard.setPenColor(color)
        self.comboBox_penColor.setCurrentIndex(self.colorList.index(color))

    def setPenThickness(self, thickness):
        self.paintBoard.setPenThickness(thickness)
        self.spinBox_penThickness.setValue(int(thickness))

    def setEraser(self, e):
        self.cbtn_Eraser.setChecked(bool(e))
        self.paintBoard.setEraser(bool(e))

    def setSettingVisible(self, v):
        self.spinBox_penThickness.setEnabled(v)#.setVisible(v)
        self.comboBox_penColor.setEnabled(v)
        self.cbtn_Eraser.setEnabled(v)
        self.btn_Clear.setEnabled(v)

    def extern_click(self, x, y):
        self.paintBoard.extern_click(x, y)

    def extern_paint(self, x, y):
        self.paintBoard.extern_paint(x, y)
        # self.update()

    def externClear(self):
        self.paintBoard.Clear()

    def resetLastPoint(self, x, y):
        self.paintBoard.resetLastPoint(x, y)

    def on_PenColorChange(self):
        color_index = self.comboBox_penColor.currentIndex()
        color_str = self.colorList[color_index]
        self.paintBoard.ChangePenColor(color_str)

    def on_PenThicknessChange(self):
        penThickness = self.spinBox_penThickness.value()
        # print('thick change to ', penThickness)
        self.paintBoard.ChangePenThickness(penThickness)

    def on_cbtn_Eraser_clicked(self):
        e = self.cbtn_Eraser.isChecked()
        self.paintBoard.setEraser(e)

    def Quit(self):
        self.close()
