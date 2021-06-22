import time

from vals.command import *
from com.protocol import encode_msg

def handle_game_time_event(server, **kwargs):
    sec = parse_game_timer_event_command(kwargs)
    server.send_all_cmd(**make_game_timer_event_command(sec))

def handle_game_timeout_event(server, **kwargs):
    inform_msg = server.ServerMessage.make_game_timeout_message()
    # 发送时间到的通告
    server.send_all_cmd(**make_inform_command(inform_msg))
    # 向当前画图者发出停止画图的指令
    server.send_cmd_by_id(id_=server.GameLogic.CurrentPaintingGamerId,
                          **make_stop_paint_command())
    time.sleep(1)

    # 设置消息循环退出flag，并放入刷新消息
    server.MessageLoopFlag = False
    server.CmdQueue.put(encode_msg(**make_break_message_loop_command()))

