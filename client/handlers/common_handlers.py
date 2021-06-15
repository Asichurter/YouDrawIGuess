from log import GlobalLogger as logger

from client.engine import ClientEngine
from client.signal import ClientSignal
from utils.handler_utils import extract_kwargs
from vals.command import parse_chat_command, parse_gamer_info_command

def handle_none(engine: ClientEngine,
                signals: ClientSignal,
                **kwargs):
    pass


# 常规聊天，不包含猜谜逻辑
def handle_common_chat(engine: ClientEngine,
                       signals: ClientSignal,
                       **kwargs):
    name, ID, content = parse_chat_command(kwargs)
    if name is None or content is None:
        logger.warning('client.handle_common_chat',
                       f'no name or content extracted: {name},{content}')
        return

    engine.add_chat_message('{}: {}'.format(name, content))


# 更新所有玩家的信息
def handle_gamer_info(engine: ClientEngine,
                      signals: ClientSignal,
                      **kwargs):
    gamers = parse_gamer_info_command(kwargs)
    if gamers is None:
        logger.warning('client.handle_gamer_info'
                       'gamers were not extracted from command body')
        return

    engine.update_gamers(gamers)
