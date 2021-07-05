import config
from vals.command import *
from vals.timer import *
from vals.entity import SERVER_CHAT_NAME
from log import GlobalLogger as logger
from com.protocol import encode_msg

def handle_make_puzzle(server, **kwargs):
    answer, hint = parse_make_puzzle_command(kwargs)
    # 将谜底和提示交给游戏逻辑实体管理
    server.GameLogic.set_answer_hint(answer, hint)
    # 启动本轮游戏的倒计时计时器，每一秒在命令队列中加入一条tick指令
    server.TimerManager.start_gametime_count_timer(
        timer_name=GAME_DOWNCOUNT_TIMER,
        msg_queue=server.CmdQueue,
        time_interval=1,
        max_ticks=config.game.RoundTime
    )
    # 将提示发送给所有玩家
    server.send_all_cmd(**make_inform_command(f'提示: {hint}'))

    logger.info('game_handlers.handle_make_puzzle',
                f'puzzle has been made, answer: {answer}, hint:{hint}')

def handle_game_chat(server, **kwargs):
    # 如果所有玩家都猜对，则终止当前游戏循环的回调函数

    name, id_, cont = parse_chat_command(kwargs)
    is_answered, answered_num = server.GameLogic.process_answer(
        answer=cont, answer_gamer_id=id_, gamer_group=server.Gamers
    )

    # 如果猜对，则发送服务器通告所有玩家，不会告知聊天信息
    if is_answered:
        logger.info('game_handlers.handle_game_chat',
                    f'gamer {name} has answered the question')
        server_chat_msg = server.ServerMessage.make_gamer_answered_inform_message(name)
        server.send_all_cmd(**make_chat_command(id_=-1,
                                                name=SERVER_CHAT_NAME,
                                                content=server_chat_msg))
        # 刷新分数
        server.send_all_cmd(**make_gamer_info_command(server.Gamers.pack_all_gamers_info()))
    # 否则将chat视为一般的聊天，广播给所有玩家
    else:
        server.send_all_cmd(**make_chat_command(id_=id_,
                                                name=name,
                                                content=cont))

    # 如果所有玩家都猜对了
    if answered_num == len(server.Gamers):
        logger.info('game_handlers.handle_game_chat',
                    f'all gamers have answered the question, this round ends')

        # 1. 终止游戏倒计时
        server.TimerManager.stop_timers_by_name(GAME_DOWNCOUNT_TIMER)
        cur_gamer = server.Gamers.get_gamer_by_id(server.GameLogic.CurrentPaintingGamerId)
        # 2. 向当前画图玩家发出停止画图的指令，向所有玩家发出当前游戏round结束的通告
        cur_gamer.send_cmd(**make_stop_paint_command())
        server.send_all_cmd(
            **make_inform_command(
                server.ServerMessage.make_all_gamers_answered_message(
                    server.GameLogic.Answer)))
        # 3. 设置flag终止消息监听循环，同时放入一条信息刷新循环判断
        server.MessageLoopFlag = False
        # 只取解码信息的body，不取包含body大小的头部信息，因为是本地的直接指令存入
        break_msg_loop_cmd, _ = encode_msg(**make_break_message_loop_command())
        server.CmdQueue.put(break_msg_loop_cmd)
        # 4. 将答案置为无效，防止其他玩家在谜底揭晓处于无效状态时进行答题
        server.GameLogic.set_answer_valid_state(False)




