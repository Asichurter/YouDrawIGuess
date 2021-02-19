import random
import time

from server.timer.count_timer import *

class TimerManager:

    def __init__(self):
        self.Timers = {}            # id-timer 映射
        self.TimerNameToId = {}     # name-idList 映射


    def gen_rand_timer_id(self):
        timer_id = random.randint(0, 6355608)
        while timer_id in self.Timers:
            timer_id = random.randint(0, 6355608)
        return timer_id


    def register_timer_name_id(self, timer, timer_name, timer_id):
        if timer_name not in self.TimerNameToId:
            self.TimerNameToId[timer_name] = [timer_id]
        else:
            self.TimerNameToId[timer_name].append(timer_id)

        self.Timers[timer_id] = timer


    def cb_clear_timer(self, timer_name, timer_id):
        def clear_timer():
            self.TimerNameToId[timer_name].remove(timer_id)
            del self.Timers[timer_id]
        return clear_timer


    # 停止所有指定名称的定时器
    def stop_timers_by_name(self, timer_name):
        for timer_id in self.TimerNameToId[timer_name]:
            self.Timers[timer_id].stop_timer()
        # 等待一个同步时间
        time.sleep(0.5)


    def add_gametime_count_timer(self, timer_name, msg_queue, time_interval, max_ticks):
        timer_id = self.gen_rand_timer_id()
        timer = GametimeCountTimer(msg_queue, time_interval, max_ticks,
                                   down_count=True)
        # 添加退出回调，定时器退出时
        timer.add_exit_callback(self.cb_clear_timer(timer_name, timer_id))
        self.register_timer_name_id(timer, timer_name, timer_id)

        timer.start(timer_id)

import queue, time

if __name__ == '__main__':
    mng = TimerManager()
    q = queue.Queue()
    mng.add_gametime_count_timer('test', q, 1, 10)
    mng.add_gametime_count_timer('test', q, 1, 10)

    for i in range(5):
        print(q.get())

    mng.stop_timers_by_name('test')
    time.sleep(2)

    print(mng.Timers)
    print(mng.TimerNameToId)



