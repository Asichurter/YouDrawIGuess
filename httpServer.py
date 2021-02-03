import socket
import time

port = 7890

class Server:
    def __init__(self, p):
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.bind(('', p))
        self.Socket.listen(5)

        self.UsrSocket = []

    def run(self):
        # self.Socket.settimeout(2)
        s, addr = self.Socket.accept()
        self.UsrSocket.append(s)
        while True:
            # try:
            #     print('listening...')
            #
            #     self.UsrSocket.append(s)
            #     print('new user connected...')
            # except socket.timeout:
            print('receiving...')
            if len(self.UsrSocket) != 0:
                self.UsrSocket[0].settimeout(2)
                try:
                    msg = self.UsrSocket[0].recv(20, socket.MSG_WAITALL)
                    print('receiving 20 bytes from host:', msg)
                except socket.timeout:
                    continue
            else:
                time.sleep(1)




if __name__ == '__main__':
    server = Server(port)
    server.run()