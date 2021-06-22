from utils.handler_utils import extract_kwargs

CMD_LOGIN = 'Login'
CMD_LOGIN_RESULT = 'LoginResult'
CMD_EXIT_LOGIN = 'ExitLogin'

CMD_CHAT = 'Chat'
CMD_GAMER_INFO = 'GamerInfo'
CMD_BEGIN_GAME = 'BeginGame'

CMD_INFORM = 'Inform'
CMD_BEGIN_PAINT = 'BeginPaint'
CMD_STOP_PAINT = 'StopPaint'
CMD_PAINT_POINT = 'PaintPoint'
CMD_CLICK_POINT = 'ClickPoint'
CMD_GAME_TIMER_EVENT = 'GameTimerEvent'
CMD_GAME_TIMEOUT_EVENT = 'GameTimeoutEvent'
CMD_END_GAME = 'EndGame'
CMD_SETTING_CHANGED = 'SettingChanged'
CMD_NEWROUND = 'NewRound'

def make_login_command(username, password):
    return {
        'command': CMD_LOGIN,
        'Username': username,
        'Password': password
    }

def parse_login_command(cmd_body):
    username = extract_kwargs(cmd_body, ('Username',), 'command.parse_login_command')
    passwd = extract_kwargs(cmd_body, ('Password',), 'command.parse_login_command')
    return username, passwd

def make_login_result_command(status_code, login_message, ID):
    return {
        'command': CMD_LOGIN_RESULT,
        'StatusCode': status_code,
        'Message': login_message,
        'ID': ID
    }

def parse_login_result_command(cmd_body):
    status_code = extract_kwargs(cmd_body, ('StatusCode',), 'command.parse_login_result_command')
    message = extract_kwargs(cmd_body, ('Message',), 'command.parse_login_result_command')
    ID = extract_kwargs(cmd_body, ('ID',), 'command.parse_login_result_command')
    return status_code, message, ID

def make_exit_login_command():
    return {
        'command': CMD_EXIT_LOGIN
    }

def make_chat_command(id_, name, content):
    return {
        'command': CMD_CHAT,
        'ID': id_,
        'Name': name,
        'Content': content
    }

def parse_chat_command(cmd_body):
    name = extract_kwargs(cmd_body, ('Name',), 'command.parse_chat_message')
    cont = extract_kwargs(cmd_body, ('Content',), 'command.parse_chat_message')
    ID = extract_kwargs(cmd_body, ('ID',), 'command.parse_chat_message')
    return name, ID, cont

def make_gamer_info_command(gamer_info):
    return {
        'command': CMD_GAMER_INFO,
        'gamers': gamer_info
    }

def parse_gamer_info_command(cmd_body):
    gamers = extract_kwargs(cmd_body, ('gamers',), 'command.parse_gamer_info_command')
    return gamers

def make_newround_command():
    return {
        'command': CMD_NEWROUND
    }

def make_inform_command(inform_msg):
    return {
        'command': CMD_INFORM,
        'content': inform_msg
    }

def parse_inform_command(cmd_body):
    inform_msg = extract_kwargs(cmd_body, ('content',), 'command.parse_inform_command')
    return inform_msg

def make_begin_paint_command():
    return {
        'command': CMD_BEGIN_PAINT
    }

def make_game_timer_event_command(sec):
    return {
        'command': CMD_GAME_TIMER_EVENT,
        'second': sec
    }

def parse_game_timer_event_command(cmd_body):
    sec = extract_kwargs(cmd_body, ('second',), 'command.prase_game_timer_event_command')
    return sec

def make_game_timeout_event_command():
    return {
        'command': CMD_GAME_TIMEOUT_EVENT
    }


