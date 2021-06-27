

class ServerMessage:
    def __init__(self):
        pass

    def make_paint_inform_message(self, gamer_name):
        return f'现在由 {gamer_name} 开始画图'

    def make_game_timeout_message(self, answer):
        return f'时间到，谜底为:{answer}'

    def make_all_gamers_answered_message(self, answer):
        return f'当前回合结束，所有玩家都猜对了{answer}'