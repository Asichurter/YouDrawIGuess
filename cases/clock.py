import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time


class MyTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 150)
        self.setWindowTitle("Alarm")
        self.setWindowIcon(QIcon('time.jpg'))

        self.lcd = QLCDNumber()
        self.lcd.setDigitCount(8)
        self.lcd.setMode(QLCDNumber.Dec)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.display(time.strftime("%X", time.localtime()))
        '''for i in range(1,3):
            self.lcd.display(i)
            time.sleep(1)'''

        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        self.setLayout(layout)

        # 新建一个QTimer对象
        # self.timer = QBasicTimer()  # QTimer()貌似不行，不知何故？
        # self.timer.start(1000, self)
        self.timerId = self.startTimer(1000)

        # 覆写计时器事件处理函数timerEvent()

    def timerEvent(self, event):
        if event.timerId() == self.timerId:#self.timer.timerId():
            self.lcd.display(time.strftime("%X", time.localtime()))

    '''else:
            super(WigglyWidget, self).timerEvent(event)'''


app = QApplication(sys.argv)
t = MyTimer()
t.show()
sys.exit(app.exec_())