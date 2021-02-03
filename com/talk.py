import json
import logging

from com.protocol import *

def recv_cmd(socket_obj):
    l_msg = b''
    remained_len = get_unreceived_header_len(len(l_msg))

    while remained_len > 0:
        l_msg += socket_obj.recv(remained_len)
        remained_len = get_unreceived_header_len(l_msg)

    # print('length msg:', l_msg)
    exp_length = decode_length(l_msg)

    cur_length = 0
    raw_msg = b''
    while cur_length < exp_length:
        # print('exp length', exp_length, 'cur lenth', cur_length)
        raw_msg += socket_obj.recv(exp_length - cur_length)
        cur_length = len(raw_msg)

    try:
        msg_body = json.loads(raw_msg)
    except json.JSONDecodeError as e:
        logging.error('[recv_cmd] Fail to decode json cmd: {}'.format(e))
        return {'command': 'none'}

    return decode_msg(msg_body)


def send_cmd(socket_obj, command, **args):
    body_msg, header_msg = encode_msg(command=command, **args)
    # 发送指令时，先发送头部，再发送主体
    socket_obj.send(header_msg)
    socket_obj.send(body_msg)