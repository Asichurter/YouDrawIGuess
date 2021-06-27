from utils.handler_utils import extract_kwargs

CMD_LOGIN = 'Login'
CMD_LOGIN_RESULT = 'LoginResult'
CMD_EXIT_LOGIN = 'ExitLogin'

CMD_CHAT = 'Chat'
CMD_GAMER_INFO = 'GamerInfo'
CMD_BEGIN_GAME = 'BeginGame'

CMD_INFORM = 'Inform'
CMD_BEGIN_PAINT = 'BeginPaint'
CMD_MAKE_PUZZLE = 'MakePuzzle'
CMD_STOP_PAINT = 'StopPaint'
CMD_BREAK_MESSAGE_LOOP = 'BreakMessageLoop'
CMD_PAINT_POINT = 'PaintPoint'
CMD_CLICK_POINT = 'ClickPoint'
CMD_GAME_TIMER_EVENT = 'GameTimerEvent'
CMD_GAME_TIMEOUT_EVENT = 'GameTimeoutEvent'
CMD_END_GAME = 'EndGame'
CMD_SETTING_CHANGED = 'SettingChanged'
CMD_NEWROUND = 'NewRound'

def make_begin_game_command():
    return {
        'command': CMD_BEGIN_GAME
    }

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

def make_begin_paint_command():
    return {
        'command': CMD_BEGIN_PAINT
    }

def make_make_puzzle_command(answer, hint):
    return {
        'command': CMD_MAKE_PUZZLE,
        'answer': answer,
        'hint': hint
    }

def parse_make_puzzle_command(cmd_body):
    answer = extract_kwargs(cmd_body, ('answer',), 'command.parse_make_puzzle_command')
    hint = extract_kwargs(cmd_body, ('hint',), 'command.parse_make_puzzle_command')
    return answer, hint

def make_stop_paint_command():
    return {
        'command': CMD_STOP_PAINT
    }

def make_break_message_loop_command():
    return {
        'command': CMD_BREAK_MESSAGE_LOOP
    }

def make_end_game_command():
    return {
        'command': CMD_END_GAME
    }

def make_click_point_command(x, y):
    return {
        'command': CMD_CLICK_POINT,
        'X': x,
        'Y': y
    }

def parse_click_point_command(cmd_body):
    x = extract_kwargs(cmd_body, ('X',), 'command.parse_click_point_command')
    y = extract_kwargs(cmd_body, ('Y',), 'command.parse_click_point_command')
    return x, y

def make_paint_point_command(points):
    return {
        'command': CMD_PAINT_POINT,
        'points': points
    }

def parse_paint_point_command(cmd_body):
    points = extract_kwargs(cmd_body, ('points',), 'command.parse_paint_point_command')
    return points

def make_setting_changed_command(kvs):
    return {
        'command': CMD_SETTING_CHANGED,
        'settings': kvs
    }

def parse_setting_changed_command(cmd_body):
    settings = extract_kwargs(cmd_body, ('settings',), 'command.parse_setting_changed_command')
    return settings

