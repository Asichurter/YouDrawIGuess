import PyQt5 as qt
from PyQt5.Qt import QWidget, QColor, QPixmap, QIcon, QSize, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QSplitter, \
    QComboBox, QLabel, QSpinBox, QLCDNumber
import PyQt5.QtCore as core

from client.comp.PaintBoard import PaintBoard, default_thickness, default_color
from utils.style_utils import get_qlabel_font_stylesheet
import config
from vals.color import INFORM_MSG_COLOR

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
        self.PaintBoard = PaintBoard(signals, Parent=self)
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
        self.InformWidget.setStyleSheet(get_qlabel_font_stylesheet(color=INFORM_MSG_COLOR, size=25))     # 设置通告栏的字体格式
        self.InformLayout.addWidget(self.InformWidget)
        self.InformClock = QLCDNumber(self)
        self.InformClock.setDigitCount(3)
        self.InformClock.setMode(QLCDNumber.Dec)
        self.InformClock.setSegmentStyle(QLCDNumber.Flat)
        self.InformLayout.addWidget(self.InformClock)
        main_layout.addLayout(self.InformLayout)
        # ---------------------------------------------------

        # 在主界面左上侧放置画板
        main_layout.addWidget(self.PaintBoard)

        # ---------------------橡皮擦--------------------------
        self.EraserCheckbox = QCheckBox("使用橡皮擦")
        self.EraserCheckbox.setParent(self)
        sub_layout.addWidget(self.EraserCheckbox)
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
        self.fill_color_list(self.comboBox_penColor, self.colorList, default_color)  # 用各种颜色填充下拉列表
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
        self.EraserCheckbox.clicked.connect(self.on_eraser_checkbox_clicked)

        # 笔划粗细改变事件处理
        self.spinBox_penThickness.valueChanged.connect(
            self.on_pen_thickness_change)  # 关联spinBox值变化信号和函数on_PenThicknessChange

        # 笔划颜色改变事件处理
        self.comboBox_penColor.currentIndexChanged.connect(
            self.on_pen_color_change)  # 关联下拉列表的当前索引变更信号与函数on_PenColorChange

        # 清空画板按钮事件处理
        self.btn_Clear.clicked.connect(self.PaintBoard.clear)

        # 退出事件处理
        # self.btn_Quit.clicked.connect(self.Quit)

    def update_inform(self, inform):
        self.InformWidget.setText(inform)

    def fill_color_list(self, comboBox, valList, defVal):
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

    def set_painting(self, painting):
        self.PaintBoard.set_paint.emit(painting)


    def set_clock_digit(self, number):
        self.InformClock.display(str(number))

    def set_pen_color(self, color):
        self.PaintBoard.set_pen_color(color)
        self.comboBox_penColor.setCurrentIndex(self.colorList.index(color))

    def set_pen_thickness(self, thickness):
        self.PaintBoard.set_pen_thickness(thickness)
        self.spinBox_penThickness.setValue(int(thickness))

    def set_eraser(self, e):
        self.EraserCheckbox.setChecked(bool(e))
        self.PaintBoard.set_eraser(bool(e))

    def set_setting_visible(self, v):
        self.spinBox_penThickness.setEnabled(v)#.setVisible(v)
        self.comboBox_penColor.setEnabled(v)
        self.EraserCheckbox.setEnabled(v)
        self.btn_Clear.setEnabled(v)

    def extern_click(self, x, y):
        self.PaintBoard.extern_click(x, y)

    def extern_paint(self, ps):
        self.PaintBoard.extern_paint(ps)
        # self.update()

    def extern_clear(self, *args, **kwargs):
        self.PaintBoard.clear()

    def resetLastPoint(self, x, y):
        self.PaintBoard.reset_last_point(x, y)

    def on_pen_color_change(self):
        color_index = self.comboBox_penColor.currentIndex()
        color_str = self.colorList[color_index]
        self.PaintBoard.change_pen_color(color_str)

    def on_pen_thickness_change(self):
        penThickness = self.spinBox_penThickness.value()
        # print('thick change to ', penThickness)
        self.PaintBoard.change_pen_thickness(penThickness)

    def on_eraser_checkbox_clicked(self):
        e = self.EraserCheckbox.isChecked()
        self.PaintBoard.set_eraser(e)

    def Quit(self):
        self.close()
