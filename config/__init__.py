
all_config = {
    'WindowSize':(1920,960),
    'PaintPanelSize':(1280, 960),
    'PaintBoardSize':(1240, 860),
    'ServerAddr':'2721988cs4.wicp.vip',
    'ServerPort':7890,
    'ServerMapPort': 44646,
    'MaxGamer':4,
    'MaxStringLength':20,
    'MinStringLength':1,
    # 'MaxMsgNumber':20,
    # 'MsgSize':5,
    'UsrAccountAddr':'account.json',
    'ServerAcceptInterval':2,       # 服务器监听3秒就去监听一次主机命令
    'HostCommandInterval':2,         # 主机命令每个循环监听2秒
    # 'HostWaitInterval':2,           # 客户端监听服务器消息和查看发送自己消息的周期
    # 'PaintWaitInterval':1,           # 服务器监听画图者发出数据的周期
    # 'ChatWaitInterval':1,           # 服务器监听聊天数据的周期
    # 'MaxGameIteration':50,          # 最大游戏周期
    'PointBufferSize':50,            # 发出缓冲区的最多的点的个数
    'GuessPointPool':[3,2,2,2,2],         # 玩家答对后的得分
    'DrawPoint':3,                  # 画出的图被猜对时画图者加分
    'RoundTime':200,                  # 每一轮的时间
    'DefaultThickness':6,
    'DefaultColor':'black'
}

class SizeConfig:
    def __init__(self):
        self.WindowSize = all_config['WindowSize']
        self.PaintPanelSize = all_config['PaintPanelSize']
        self.PaintBoardSize = all_config['PaintBoardSize']

size = SizeConfig()


class ConnectConfig:
    def __init__(self):
        self.ServerAddr = all_config['ServerAddr']
        self.ServerPort = all_config['ServerPort']
        self.ServerMapPort = all_config['ServerMapPort']

connect = ConnectConfig()


class GameConfig:
    def __init__(self):
        self.MaxGamer = all_config['MaxGamer']
        self.MaxStringLength = all_config['MaxStringLength']
        self.MinStringLength = all_config['MinStringLength']
        self.GuessPointPool = all_config['GuessPointPool']
        self.DrawPoint = all_config['DrawPoint']
        self.RoundTime = all_config['RoundTime']

game = GameConfig()


class ServerConfig:
    def __init__(self):
        self.MaxGamer = all_config['MaxGamer']
        self.UsrAccountAddr = all_config['UsrAccountAddr']
        self.ServerAcceptInterval = all_config['ServerAcceptInterval']
        self.HostCommandInterval = all_config['HostCommandInterval']


server = ServerConfig()


class ClientConfig:
    def __init__(self):
        self.PointBufferSize = all_config['PointBufferSize']

client = ClientConfig()


class PaintConfig:
    def __init__(self):
        self.DefaultThickness = all_config['DefaultThickness']
        self.DefaultColor = all_config['DefaultColor']

paint = PaintConfig()



