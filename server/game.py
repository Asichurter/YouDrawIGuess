import config

class GameLogic:
    def __init__(self, gamer_num):
        self.GamerNum = gamer_num
        self.PointPool = config.game.GuessPointPool
        self.PointIndex = 0
        self.Answer = ''
        self.Hint = ''
        self.AnsweredGamerIds = []
        self.reset_point_pool()

    def init_game_state(self):
        self.reset_point_pool()
        self.AnsweredGamerIds.clear()

    def add_answered_gamer_id(self, id_):
        self.AnsweredGamerIds.append(id_)

    def reset_point_pool(self):
        self.PointIndex = 0

    def get_next_point(self):
        assert self.PointIndex < self.GamerNum, '[Game] point access time exceeds gamer number'
        p = self.PointPool[self.PointIndex]
        self.PointIndex += 1
        return p

    def set_answer_hint(self, a, h):
        self.Answer = a
        self.Hint = h

    def check_answer(self, a):
        return self.Answer == a

    def get_hint(self):
        return self.Hint



