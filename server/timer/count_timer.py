

from server.timer.base_timer import BaseTimer
from com.talk import encode_msg

class TimeCountTimer(BaseTimer):

    def __init__(self, time_interval, max_ticks, down_count=True):
        super(TimeCountTimer, self).__init__(time_interval, max_ticks)
        self.DownCount = down_count


    def tick_event(self, tick, *args, **kwargs):
        if self.DownCount:
            time_count = self.Interval * (self.MaxTicks - tick)
        else:
            time_count = self.Interval * tick

        self.process_count(time_count)

    # 子类中需要实现的方法
    # 提供了时间刻度
    def process_count(self, time_count):
        pass



class GametimeCountTimer(TimeCountTimer):

    def __init__(self, msg_queue, time_interval, max_ticks, down_count=True):
        super(GametimeCountTimer, self).__init__(time_interval, max_ticks, down_count)
        self.Queue = msg_queue

    # 实际的时间戳处理函数
    # 将一条带有time事件的信息放入队列进行消费
    def process_count(self, time_count):
        msg, _ = encode_msg(command='TimerEvent',
                         second=str(time_count))
        self.Queue.put(msg)


    # 超时事件处理函数
    # 将一条带有timeout事件的信息放入队列进行消费
    def timeout_event(self, tick, *args, **kwargs):
        msg, _ = encode_msg('Timeout')
        self.Queue.put(msg)

# import queue
# import time
#
# if __name__ == '__main__':
#     q = queue.Queue()
#     timer = GametimeCountTimer(q, 1, 10, down_count=True)
#     timer.start(0)
#
#     for i in range(5):
#         msg = q.get()
#         print(msg)
#
#     timer.stop_timer()
#     time.sleep(3)

