

class ServerHandlingError(Exception):
    def __init__(self, cmd, cmd_body, msg):
        self.Cmd = cmd
        self.CmdBody = cmd_body
        self.Message = msg

    def __repr__(self):
        return f'Cmd: {self.Cmd}, msg: {self.Message}, cmd_body:{self.CmdBody}'

class DecodeError(Exception):
    def __init__(self, raw_msg, err_msg):
        self.RawMessage = raw_msg
        self.ErrMessage = err_msg

    def __repr__(self):
        return f'Raw Message: {self.RawMessage}, error message: {self.ErrMessage}'
