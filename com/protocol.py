import json
import logging

CodingFormat = 'UTF-8'
HeaderDummy = b'{"len": "0000"}'
HeaderLength = len(HeaderDummy)

from log import GlobalLogger as logger
from vals.error import DecodeError


def _make_len_header(body_len, digit_num=4):
    return json.dumps({'len': ('%%0%dd' % digit_num) % body_len})


def get_unreceived_header_len(cur_msg):
    return HeaderLength - len(cur_msg)


def encode_msg(command, **kwargs):
    body = {k:v for k,v in kwargs.items()}
    body['command'] = command

    body_msg = json.dumps(body).encode(CodingFormat)
    header_msg = _make_len_header(len(body_msg)).encode(CodingFormat)#('Length %04d'%len(msg)).encode(CodingFormat)

    return body_msg, header_msg

def decode_length(length_header):
    try:
        length_header = json.loads(length_header.decode(CodingFormat))
    except json.JSONDecodeError as e:
        logger.error('protocol.decode_length',
            '[decode_length] Fail to decode length header: {}'.format(e))
        return 0

    return int(length_header.get('len', 0))

def decode_msg(raw_msg_body, raise_exception=False) -> (str, dict):
    try:
        msg_body = json.loads(raw_msg_body)
        command = msg_body.pop('command')
        return command, msg_body
    except json.JSONDecodeError as e:
        if raise_exception:
            raise DecodeError(raw_msg_body, str(e))
        logger.error('protocol.decode_msg',
                     'Fail to decode msg body: {}'.format(e))

        return 'unknown', {}
    except Exception as ue:
        if raise_exception:
            raise DecodeError(raw_msg_body, str(ue))
        logger.error('protocol.decode_msg',
                     'unknown err: {}, raw_msg: {}'.format(ue, msg_body))
        return 'unknown', {}
    #
    #
    #
    # lines = msg_body.split('\n')
    #
    # command = lines[0]
    # args = {}
    #
    # for l in lines[1:]:
    #     words = l.split(' ')
    #     key = words[0]
    #     value = ' '.join(words[1:])
    #     args[key] = value
    #
    # return command, args