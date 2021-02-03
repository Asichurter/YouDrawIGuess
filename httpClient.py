import socket

addr = ('103.46.128.45', 36654)

class Client:
    def __init__(self):
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.connect(addr)

    def run(self):
        while True:
            input('>> ')
            msg = b'11111111122221333311'
            print('sending length:', len(msg))
            self.Socket.send(msg)



if __name__ == "__main__":
    client = Client()
    client.run()