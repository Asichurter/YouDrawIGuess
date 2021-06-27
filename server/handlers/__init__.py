from .login_handlers import *
from .common_handlers import *
from .game_handlers import *
from .timer_handlers import *

from log import GlobalLogger as logger
from vals.command import *
from vals.state import *

# 直接转发handler的过滤器之一,将当前gamer过滤掉
def cur_gamer_id_filter(cur_gamer, gamer):
    return not cur_gamer.Id == gamer.Id

__handler_switch = {
    # handler输入要求：
    # 1. cmd_body的kv解引用参数
    # 2. gamer的当前操作玩家，kv参数
    S_LOGIN_STATE: {
        CMD_BEGIN_GAME: handle_game_begin,
        CMD_LOGIN: handle_gamer_login,
        CMD_EXIT_LOGIN: handle_gamer_exit_login,
    },
    # handler输入要求：
    # 1. cmd_body的kv解引用参数
    # 2. cur_gamer的当前画图玩家，kv参数
    # 3. raw_message的指令源数据，kv参数
    S_GAME_STATE: {
        CMD_CHAT: handle_game_chat,
        CMD_MAKE_PUZZLE: handle_make_puzzle,
        CMD_BREAK_MESSAGE_LOOP: handle_none,    # 消息循环刷新判断用信息，不做任何操作
        CMD_GAME_TIMER_EVENT: handle_game_time_event,
        CMD_GAME_TIMEOUT_EVENT: handle_game_timeout_event,
        CMD_PAINT_POINT: get_simple_forward_handler(cur_gamer_id_filter),
        CMD_CLICK_POINT: get_simple_forward_handler(cur_gamer_id_filter),
        CMD_SETTING_CHANGED: get_simple_forward_handler(cur_gamer_id_filter)
    }
}

def get_handler(state, cmd, supress_log=False):
    logger.debug('server.handlers',
                 'getting handler of {}'.format(cmd))
    try:
        handler = __handler_switch[state][cmd]
        return handler
    except KeyError:
        if not supress_log:
            logger.warning('server.handlers.get_handler',
                         'can not get handler for {c} in {s}'.format(c=cmd, s=state))
        return handle_none
    except Exception as e:
        if not supress_log:
            logger.error('server.handlers.get_handler',
                         'unknown err: {}'.format(e))
        return handle_none
