

class State:
    def __init__(self):
        self.Commmands = None
        self.Handlers = None

    def process(self, msg):
        raise NotImplementedError

class SLoginState(State):
    def __init__(self, handlers):
        super.__init__()
        self.Commands = ['login']
        self.Handlers = {}.fromkeys(self.Commands)

    def process(self, msg):
        pass

    def checkLogin(self):
        pass
