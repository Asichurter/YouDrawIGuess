from log import GlobalLogger as logger
# from server.core import Server
from utils.handler_utils import extract_kwargs
from vals.command import parse_chat_command, make_chat_command
from com.protocol import decode_msg


# 常规聊天，不包含猜谜逻辑
def handle_common_chat(server,
                      **kwargs):
    name, ID, content = parse_chat_command(kwargs)
    if name is None or content is None:
        logger.warning('common_handlers.handle_common_chat',
                       f'no name or content extracted: {name},{content}')
        return

    server.send_all_cmd(**make_chat_command(ID, name, content))

def get_simple_forward_handler(gamer_filter=None):
    # gamer_filter
    # 输入：(当前gamer，遍历的gamer)
    # 输出：是否通过过滤检查的bool类型
    def handle_simple_forward(server, **kwargs):
        raw_message = extract_kwargs(kwargs, ('raw_message',), 'common_handlers.handle_simple_forward')
        cur_gamer = extract_kwargs(kwargs, ('cur_gamer',), 'common_handlers.handle_simple_forward')
        raw_cmd, raw_cmd_body = decode_msg(raw_message)

        for gamer in server.Gamers:
            # 检查gamer
            if gamer_filter is not None:
                if not gamer_filter(cur_gamer, gamer):
                    continue

            # 直接转发之
            gamer.send_cmd(command=raw_cmd, **raw_cmd_body)

    return handle_simple_forward





# # 更新所有玩家的信息
# def handle_gamer_info(server: Server,
#                       **kwargs:
#
#     gamers = extract_kwargs(kwargs, ('gamers', 'Gamers'), 'client.handlers.handle_gamer_info')
#     if gamers is None:
#         return
#
#     engine.update_gamers(gamers)

