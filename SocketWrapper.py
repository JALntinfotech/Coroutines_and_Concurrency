from Promise_Architecture import ReadWait, WriteWait


class Socket(object):
    def __init__(self, socket):
        self.socket = socket

    def accept(self):
        yield ReadWait(self.socket)
        client, address = self.socket.accept()
        yield Socket(client), address

    def send(self, buffer):
        while buffer:
            yield WriteWait(self.socket)
            length = self.socket.send(buffer)
            buffer = buffer[length:]

    def receive(self, maxbytes):
        yield ReadWait(self.socket)
        yield self.socket.recv(maxbytes)

    def close(self):
        yield self.socket.close()
