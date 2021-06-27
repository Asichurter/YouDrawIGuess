from .common_handlers import *
from .ready_handler import *
from .game_handler import *

from log import GlobalLogger as logger
from vals.command import *
from vals.state import *

__handler_switch = {
    C_WAIT_FOR_READY_STATE: {
        CMD_CHAT: handle_common_chat,
        CMD_GAMER_INFO: handle_gamer_info,
        CMD_BEGIN_GAME: handle_begin_game
    },
    C_GAME_STATE: {
        CMD_CHAT: handle_common_chat,
        CMD_GAMER_INFO: handle_gamer_info,
        CMD_INFORM: handle_inform,
        CMD_BEGIN_PAINT: handle_begin_paint,
        CMD_STOP_PAINT: handle_stop_paint,
        CMD_PAINT_POINT: handle_paint_point,
        CMD_CLICK_POINT: handle_click_point,
        CMD_NEWROUND: handle_new_round,
        CMD_GAME_TIMER_EVENT: handle_game_timer_event,
        CMD_END_GAME: handle_end_game,
        CMD_SETTING_CHANGED: handle_setting_changed
    }
}

def get_handler(state, cmd):
    logger.debug('client.handlers',
                 'getting handler of {}'.format(cmd))
    try:
        handler = __handler_switch[state][cmd]
        return handler
    except KeyError:
        logger.error('client.handlers.get_handler',
                     'can not get handler for {}.{}'.format(state, cmd))
        return handle_none
    except Exception as e:
        logger.error('client.handlers.get_handler',
                     'unknown err: {}'.format(e))
        return handle_none
