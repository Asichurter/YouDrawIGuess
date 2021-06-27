import time

from vals.command import *
from com.protocol import encode_msg

#####################################################################
# 每一轮游戏倒计时的每一秒的时间事件处理
# 处理方式是将秒数发送给所有玩家显示在LED上
#####################################################################
def handle_game_time_event(server, **kwargs):
    sec = parse_game_timer_event_command(kwargs)
    server.send_all_cmd(**make_game_timer_event_command(sec))

#####################################################################
# 每一轮游戏倒计时的时间到事件处理
# 1. 发送时间到的通告
# 2. 向当前画图者发出停止画图的指令
# 3. 设置flag来退出本轮游戏的消息监听循环
#####################################################################
def handle_game_timeout_event(server, **kwargs):
    inform_msg = server.ServerMessage.make_game_timeout_message(server.GameLogic.Answer)
    # 发送时间到的通告,顺便告知正确答案
    server.send_all_cmd(**make_inform_command(inform_msg))
    # 向当前画图者发出停止画图的指令
    server.send_cmd_by_id(id_=server.GameLogic.CurrentPaintingGamerId,
                          **make_stop_paint_command())
    time.sleep(1)

    # 设置消息循环退出flag，并放入刷新消息
    server.MessageLoopFlag = False
    server.CmdQueue.put(encode_msg(**make_break_message_loop_command()))

