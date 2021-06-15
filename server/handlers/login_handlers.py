from server.core import Server
from vals.command import CMD_BEGIN_GAME
from utils.handler_utils import extract_kwargs
from server.gamer import Gamer
from  vals.command import parse_login_command, make_login_result_command

from log import GlobalLogger as logger

def handle_none(server: Server,
                **kwargs):
    pass

# 处理服务器端游戏开始指令
def handle_game_begin(server: Server,
                      **kwargs):
    logger.info('server.login_state', 'game is begun')
    # 设置游戏开始flag，停止接受更多玩家连接
    server.GameBeginFlag.write_val(False)
    # 向所有玩家发送游戏开始指令
    server.send_all_cmd_unlogged(CMD_BEGIN_GAME)

def handle_gamer_login(server: Server,
                       **kwargs):
    username, passwd = parse_login_command(kwargs)
    gamer = extract_kwargs(kwargs, ('Gamer', 'gamer'), 'server.login_handler')
    passed, login_msg, gamer_id = server.GamerAccount.check_gamer_login(username, passwd)

    gamer.send_cmd(**make_login_result_command(
        status_code=1 if passed else 0,
        login_message=login_msg,
        ID = gamer_id
    ))

    if passed:
        new_gamer = Gamer(gamer, gamer_id, username)
        server.add_gamer(new_gamer)
        server.send_gamer_info()
        gamer.LoginFlag.write_val(True)      # 登录成功后将flag标志为True告知外部可以退出登录循环

        logger.info('server.login', 'gamer {}:{} login'.format(gamer_id, username))

def handle_gamer_exit_login(server: Server,
                            **kwargs):
    gamer = extract_kwargs(kwargs, ('Gamer', 'gamer'), 'server.login_handler')
    gamer.LoginFlag.write_val(True)      # 玩家主动退出登录操作也需要标志为True退出登录循环



