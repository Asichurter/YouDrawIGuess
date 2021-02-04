from client.engine import ClientEngine
from client.signal import ClientSignal
from client.handlers.util import extract_kwargs

from log import GlobalLogger as logger
from com.command import *

GAME_END_FLAG = '__GAME_END__'

def check_game_is_end(flag):
    return type(flag) == str and flag == GAME_END_FLAG


# 处理服务器发来的通知消息
def handle_inform(engine: ClientEngine,
                  signals: ClientSignal,
                  **kwargs):
    inform = extract_kwargs(kwargs, ('Inform', 'inform'))
    if inform is None:
        return

    engine.update_inform(inform)


# 处理本玩家开始绘图的指令
def handle_begin_paint(engine: ClientEngine,
                       signals: ClientSignal,
                       **kwargs):

    engine.Panel.set_painting(True)
    engine.Panel.State = 'painting'
    answer = engine.Panel.get_input_by_dialog(
        '出题',
        '请输入谜底',
        '谜底不能为空',
        True,
        lambda s: len(s) <= 20,
        '谜底长度不能超过20个字符'
    )
    hint = engine.Panel.get_input_by_dialog(
        '出题',
        '请输入提示',
        '',
        False,
        lambda s: len(s) <= 20,
        '提示长度不能超过20个字符'
    )

    logger.info('client.handlers.handle_begin_paint',
                '谜题: {}, 提示: {}'.format(answer, hint))

    engine.send_cmd(command=CMD_BEGIN_PAINT, answer=answer, hint=hint)
    # 只有要画图的人才能看到设置面板
    engine.Panel.PaintPanel.set_setting_visible(True)


# 处理本玩家停止绘图的指令
def handle_stop_paint(engine: ClientEngine,
                      signals: ClientSignal,
                      **kwargs):

    engine.Panel.set_painting(False)
    engine.Panel.State = 'Waiting'


# 处理绘图事件指令，一次性绘制多个点
def handle_paint_point(engine: ClientEngine,
                       signals: ClientSignal,
                       **kwargs):

    points = extract_kwargs(kwargs, ('points', 'Points'))
    if points is None:
        return

    engine.Panel.PaintPanel.extern_paint(points)


# 处理鼠标点击，开始绘图事件
def handle_click_point(engine: ClientEngine,
                       signals: ClientSignal,
                       **kwargs):

    x = extract_kwargs(kwargs, ('X', 'x'))
    y = extract_kwargs(kwargs, ('Y', 'y'))
    if x is None or y is None:
        return

    engine.Panel.PaintPanel.extern_click(x, y)


# 处理计时器事件，更新时间显示
def handle_timer_event(engine: ClientEngine,
                       signals: ClientSignal,
                       **kwargs):
    digit = extract_kwargs(kwargs, ('Second', 'second'))
    if digit is None:
        return

    engine.Panel.PaintPanel.set_clock_digit(digit)


# 处理游戏结束指令
def handle_end_game(engine: ClientEngine,
                    signals: ClientSignal,
                    **kwargs):
    return GAME_END_FLAG


# 改变设置的函数映射
SettingChangeSwitch = {
    'Color': lambda e,v: e.Panel.PaintPanel.set_pen_color(v),
    'Thickness': lambda e,v: e.Panel.PaintPanel.set_pen_thickness(v),
    'Eraser': lambda e,v: e.Panel.PaintPanel.set_eraser(v),
    'Clear': lambda e,v: e.Panel.PaintPanel.extern_clear()
}
EmptySettingChangedHandler = lambda e,v: None

# 处理设置变化的事件，如橡皮擦修改，颜色修改，粗细修改和清空等
def handle_setting_changed(engine: ClientEngine,
                           signals: ClientSignal,
                           **kwargs):

    for k, v in kwargs.items():
        SettingChangeSwitch.get(k, EmptySettingChangedHandler)(engine, v)


# 处理开始新一轮游戏的指令
def handle_new_round(engine: ClientEngine,
                     signals: ClientSignal,
                     **kwargs):

    engine.Panel.reset_paint_panel()
