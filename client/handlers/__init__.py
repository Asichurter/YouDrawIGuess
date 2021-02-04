from .common_handlers import *
from .ready_handler import *
from .game_handler import *

from log import GlobalLogger as logger
from com.command import *

handler_switch = {
    'wait_for_ready': {
        CMD_CHAT: handle_common_chat,
        CMD_GAMER_INFO: handle_gamer_info,
        CMD_BEGIN_GAME: handle_begin_game
    },
    'game': {
        CMD_CHAT: handle_common_chat,
        CMD_GAMER_INFO: handle_gamer_info,
        CMD_INFORM: handle_inform,
        CMD_BEGIN_PAINT: handle_begin_paint,
    }
}

def get_handler(state, cmd):
    try:
        handler = handler_switch[state][cmd]
        return handler
    except KeyError:
        logger.error('client.handlers.get_handler',
                     'can not get handler for {}.{}'.format(state, cmd))
        return handle_none
