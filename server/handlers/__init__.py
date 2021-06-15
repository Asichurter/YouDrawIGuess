from .login_handlers import *

from log import GlobalLogger as logger
from vals.command import *
from vals.state import *

__handler_switch = {
    S_LOGIN: {
        CMD_BEGIN_GAME: handle_game_begin,
        CMD_LOGIN: handle_gamer_login,
        CMD_EXIT_LOGIN: handle_gamer_exit_login,
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
