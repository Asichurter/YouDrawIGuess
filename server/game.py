import config
from log import GlobalLogger as logger

class GameLogic:
    def __init__(self, gamer_num):
        self.GamerNum = gamer_num
        self.PointPool = config.game.GuessPointPool
        self.PointIndex = 0
        self.Answer = ''
        self.Hint = ''
        self.IsAnswerValid = True
        self.AnsweredGamerIds = []
        self.CurrentPaintingGamerId = None      # 当前画图的玩家的ID
        self.reset_point_pool()

    def init_game_state(self, cur_painting_gamer_id):
        self.reset_point_pool()
        self.AnsweredGamerIds.clear()
        self.set_current_painting_gamer_id(cur_painting_gamer_id)

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
        self.IsAnswerValid = True

    def set_current_painting_gamer_id(self, id_):
        self.CurrentPaintingGamerId = id_

    def set_answer_valid_state(self, is_valid):
        self.IsAnswerValid = is_valid

    def check_answer(self, a):
        return self.Answer == a

    def check_gamer_is_answered(self, gamer_id):
        return gamer_id in self.AnsweredGamerIds

    def get_hint(self):
        return self.Hint

    def process_answer(self, answer, answer_gamer_id, gamer_group):
        logger.debug('GameLogic.process_answer',
                     f'state: {self.IsAnswerValid}, {answer} : {self.Answer}')
        # 问题处于无效状态时不做判断
        if not self.IsAnswerValid:
            return False, len(self.AnsweredGamerIds)

        if not self.check_gamer_is_answered(answer_gamer_id) and self.check_answer(answer):
            ans_gamer = gamer_group.get_gamer_by_id(answer_gamer_id)
            pat_gamer = gamer_group.get_gamer_by_id(self.CurrentPaintingGamerId)
            logger.info('handlers.handle_game_chat',
                        f'gamer {ans_gamer.UserName} has answered this puzzle')
            # 将答对的玩家的id加入到已完成回答的列表中
            self.add_answered_gamer_id(answer_gamer_id)
            # 答题玩家和画图玩家都得分
            ans_gamer.score(self.get_next_point())
            pat_gamer.score(config.game.DrawPoint)
            return True, len(self.AnsweredGamerIds)
        else:
            return False, len(self.AnsweredGamerIds)






