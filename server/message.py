

class ServerMessage:
    def __init__(self):
        pass

    def make_paint_inform_message(self, gamer_name):
        return f'现在由 {gamer_name} 开始画图'

    def make_game_timeout_message(self):
        return '时间到'