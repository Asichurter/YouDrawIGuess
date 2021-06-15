from log import GlobalLogger as logger
from server.core import Server
from utils.handler_utils import extract_kwargs
from vals.command import parse_chat_command, make_chat_command


# 常规聊天，不包含猜谜逻辑
def handle_common_chat(server: Server,
                      **kwargs):
    name, ID, content = parse_chat_command(kwargs)
    if name is None or content is None:
        logger.warning('client.handle_common_chat',
                       f'no name or content extracted: {name},{content}')
        return

    server.send_all_cmd(**make_chat_command(ID, name, content))


# # 更新所有玩家的信息
# def handle_gamer_info(server: Server,
#                       **kwargs:
#
#     gamers = extract_kwargs(kwargs, ('gamers', 'Gamers'), 'client.handlers.handle_gamer_info')
#     if gamers is None:
#         return
#
#     engine.update_gamers(gamers)
