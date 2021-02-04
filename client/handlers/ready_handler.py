from client.engine import ClientEngine
from client.signal import ClientSignal
from client.handlers.util import extract_kwargs

BEGIN_GAME_FALG = '__BEGIN_GAME__'

def check_game_is_begin(flag):
    return type(flag) == str and flag == BEGIN_GAME_FALG


def handle_begin_game(engine: ClientEngine,
                      signals: ClientSignal,
                      **kwargs):
    return BEGIN_GAME_FALG
