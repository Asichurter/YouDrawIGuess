import threading
import time

class BaseTimer:
    def __init__(self, time_interval, max_ticks):
        self.Interval = time_interval
        self.MaxTicks = max_ticks
        self.TimerId = None
        self.TimerThread = None

        self.Eps = 5e-2

        self.TimerStopFlag = False
        self.ExitCallbacks = []


    def start(self, timer_id, *args, **kwargs):
        self.TimerId = timer_id
        self.TimerThread = threading.Thread(None,
                                            target=self.timer_thread,
                                            args=args,
                                            kwargs=kwargs)
        self.TimerThread.start()


    def timer_thread(self, *args, **kwargs):
        tick = 0
        while tick < self.MaxTicks \
                and self.check_condition(tick, *args, **kwargs)\
                and self.check_stop_flag():
            time.sleep(self.Interval - self.Eps)    # 为处理事件提供缓冲空间
            tick += 1
            self.tick_event(tick, *args, **kwargs)


        if tick == self.MaxTicks:
            self.timeout_event(tick, *args, **kwargs)
        else:
            self.early_exit_event(tick, *args, **kwargs)

        # 线程结束以后清空线程上下文
        self.TimerThread = None
        self.TimerId = None

        for exit_callback in self.ExitCallbacks:
            exit_callback()

    # 子类中需要实现的方法
    # 在定时器时间刻度到达时触发
    def tick_event(self, tick, *args, **kwargs):
        pass


    # 子类中需要实现的方法
    # 在定时器超时时触发
    def timeout_event(self, tick, *args, **kwargs):
        pass


    # 子类中需要实现的方法
    # 在定时器由于条件检测失败提前终止的方法
    def early_exit_event(self, tick, *args, **kwargs):
        pass


    # 子类中需要实现的方法
    # 用于在时间刻度上轮训计时器条件，判断是否提前退出计时器
    def check_condition(self, tick, *args, **kwargs):
        return True


    def check_stop_flag(self):
        return not self.TimerStopFlag


    def stop_timer(self):
        self.TimerStopFlag = True


    def add_exit_callback(self, cb):
        self.ExitCallbacks.append(cb)


    # 设置定时器间隔休眠的调整数值，调整给其他处理函数留出处理的时间
    def set_eps(self, eps):
        self.Eps = eps


