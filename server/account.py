from threading import Lock

from utils.file_utils import loadJson
from log import GlobalLogger as logger

class GamerAccount:
    def __init__(self, pth):
        self.LoggedGamers = []
        self.Lock = Lock()
        try:
            self.Accounts = loadJson(pth)
        except Exception as e:
            logger.critical('server.account',
                            'fail to load gamer account: %s' % str(e))
            self.Accounts = {}

    def check_gamer_login(self, username, passwd):
        if username not in self.Accounts:
            return False, '用户不存在', -1
        elif username in self.LoggedGamers:
            return False, '用户已登录', -1
        elif self.Accounts[username] != passwd:
            return False, '密码不正确', -1
        else:
            self.Lock.acquire()
            gamer_id = len(self.LoggedGamers)
            self.LoggedGamers.append(username)  # 已登录的玩家添加到account的列表中便于查询
            self.Lock.release()
            return True, '登陆成功', gamer_id
