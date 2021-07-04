# from server.core import Server
from vals.command import CMD_BEGIN_GAME
from utils.handler_utils import extract_kwargs
from vals.command import *
from log import GlobalLogger as logger

def handle_none(server,
                **kwargs):
    pass

# 处理服务器端游戏开始指令
def handle_game_begin(server,
                      **kwargs):
    logger.info('server.handle_game_begin', 'game is begun')
    # 设置游戏开始flag，停止接受更多玩家连接
    server.GameBeginFlag.write_val(False)
    # 向所有玩家发送游戏开始指令
    server.send_all_cmd_unlogged(**make_begin_game_command())

def handle_gamer_login(server,
                       **kwargs):
    gamer = extract_kwargs(kwargs, ('Gamer', 'gamer'), 'server.login_handler')
    # 首先检查玩家数量是否超过限制
    with server.Gamers as gp:
        is_gamer_enough = gp.check_gamer_is_enough()
        if is_gamer_enough:
            fail_cmd = make_login_result_command(
                status_code=0,
                login_message='玩家数量超过限制',
                ID=-1
            )
            gamer.send_cmd(**fail_cmd)
            return

    username, passwd = parse_login_command(kwargs)
    passed, login_msg, gamer_id = server.GamerAccount.check_gamer_login(username, passwd)

    cmd = make_login_result_command(
        status_code=1 if passed else 0,
        login_message=login_msg,
        ID=gamer_id
    )
    logger.debug('handlers.handle_gamer_login',
                 f'send msg: {cmd}')

    if passed:
        from server.gamer import Gamer      # 逻辑内部import，防止循环import问题
        new_gamer = Gamer(gamer, gamer_id, username)
        with server.Gamers as gp:
            # 首先发送登录结果信息
            gamer.send_cmd(**cmd)
            gp.add_gamer(new_gamer, gamer_id, safe_call=True)
            # 然后发送所有玩家信息，更新玩家情况
            gamers_info = gp.pack_all_gamers_info()
            server.send_all_cmd(**make_gamer_info_command(gamers_info))

        # 登录成功后将flag标志为True告知外部可以退出登录循环
        gamer.LoginFlag.write_val(True)
        logger.info('server.login', 'gamer {}:{} login'.format(gamer_id, username))
    else:
        # 不通过也要发送登录结果
        gamer.send_cmd(**cmd)


def handle_gamer_exit_login(server,
                            **kwargs):
    gamer = extract_kwargs(kwargs, ('Gamer', 'gamer'), 'server.login_handler')
    gamer.LoginFlag.write_val(True)      # 玩家主动退出登录操作也需要标志为True退出登录循环



