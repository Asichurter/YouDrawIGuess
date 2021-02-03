'''
    @Author: 唐郅杰

    This module is for configuring the program settings by a config manager.
    The manager is responsable to read configurations from config file and
    save the changes to file. Config values are accessible through config
    manager.

    The usable settings will be contained in an independent class called
    ConfigSet and the management of configs belong to a class called
    ConfigManager.
'''

import json

DefaultConfigSet = {
    'WindowSize':(1920,960),
    'PaintPanelSize':(1280, 960),
    'PaintBoardSize':(1240, 860),
    'ServerAddr':'2721988cs4.wicp.vip',
    'ServerPort':7890,
    'MaxGamer':4,
    'MaxStringLength':20,
    'MinStringLength':1,
    'MaxMsgNumber':20,
    'MsgSize':5,
    'UsrAccountAddr':'account.json',
    'ServerAcceptInterval':2,       # 服务器监听3秒就去监听一次主机命令
    'HostCommandInterval':2,         # 主机命令每个循环监听2秒
    'HostWaitInterval':2,           # 客户端监听服务器消息和查看发送自己消息的周期
    'PaintWaitInterval':1,           # 服务器监听画图者发出数据的周期
    'ChatWaitInterval':1,           # 服务器监听聊天数据的周期
    'MaxGameIteration':50,          # 最大游戏周期
    'PointBufferSize':50,            # 发出缓冲区的最多的点的个数
    'GuessPointPool':[3,2,2,2,2],         # 玩家答对后的得分
    'DrawPoint':3,
    'RoundTime':200,                  # 每一轮的时间
    'DefaultThickness':6,
    'DefaultColor':'black'
}

ConnectionConfig = {
    'ConnectingFailureCode':500,
    'ConnectingFailureMsg':'Too many connections'
}

# class ConfigSet:
#
#     def __init__(self):
#         self.MaxFileSize = 50
#         self.ValueVisible = True
#         self.DifferentialVisible = True
#         self.IntegrateVisible = True
#         self.ValueMarker = True
#         self.DifferentialMarker = True
#         self.IntegrateMarker = True
#         self.ShowGrid = True
#         self.PlotBgColor = [0, 0, 0]  # white bg in default
#         self.PlotCurveColor = [255, 255, 255]  # black curve in default
#         self.Marker = 'o'
#         self.MarkerColor = [0, 0, 255]
#         self.WindowWidth = 1800
#         self.WindowHeight = 1400
#         self.PlotWidth = 1500
#         self.PlotHeight = 400
#         self.LabelOneFontStyle = "QLabel{color:rgb(0,0,200);font-size:20px;font-weight:normal;font-family:Arial;}"
#         self.LabelTwoFontStyle = "QLabel{color:rgb(0,0,0);font-size:15px;font-weight:normal;font-family:Arial;}"
#         self.LabelThreeFontStyle = "QLabel{color:rgb(0,0,0);font-size:18px;font-weight:normal;font-family:Arial;}"
#         self.IconPath = 'icon.png'
#
#     def items(self):
#         return self.__dict__.items()
#
#     def keys(self):
#         return self.__dict__.keys()
#
#     def set(self, k, v):
#         try:
#             self.__dict__[k] = v
#             return True
#         except KeyError:
#             return False


class CongfigManager:

    def __init__(self, configPath='config.json'):
        # self.defaultConfig = ConfigSet()
        self.readConfig = self.loadConfig(configPath)

    def loadConfig(self, path):
        if not path.endswith('.json'):
            return DefaultConfigSet
        try:
            with open(path, 'r') as f:
                configs = json.load(f)
                configs = self.checkAndCorrectConfig(configs)
                return configs
        except:
            return DefaultConfigSet

    def checkAndCorrectConfig(self, config):
        '''
            Check the attributes and values in read config, correct the
            illegal value and complement the missing attributes.
        '''
        checkedConfig = config

        for k, dv in DefaultConfigSet.items():
            if k not in checkedConfig.keys():  # expected value not exist in read configs
                checkedConfig[k] = dv

            elif type(checkedConfig[k]) != type(dv):  # illegal data type found in read configs
                print('illegal key in config', k)
                checkedConfig[k] = dv

        for ck in checkedConfig.keys():
            if ck not in DefaultConfigSet.keys():  # remove the redundant items
                del checkedConfig[ck]

        return checkedConfig

    def get(self, name):
        return self.readConfig[name]








