from client.engine import ClientEngine
from client.signal import ClientSignal
from client.handlers.util import extract_kwargs


def handle_none(engine: ClientEngine,
                signals: ClientSignal,
                **kwargs):
    pass


# 常规聊天，不包含猜谜逻辑
def handle_common_chat(engine: ClientEngine,
                       signals: ClientSignal,
                       **kwargs):
    name = extract_kwargs(kwargs, ('name', 'Name'))
    content = extract_kwargs(kwargs, ('content', 'Content'))

    if name is None or content is None:
        return

    engine.add_chat_message('{}: {}'.format(name, content))


# 更新所有玩家的信息
def handle_gamer_info(engine: ClientEngine,
                      signals: ClientSignal,
                      **kwargs):
    gamers = extract_kwargs(kwargs, ('gamers', 'Gamers'))
    if gamers is None:
        return

    engine.update_gamers(gamers)
