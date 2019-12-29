from pyos import system_call


class Socket(object):
    def __init__(self, sock):
        self.sock = sock

    def accept(self):
        yield system_call.ReadWait(self.sock)
        client, addr = self.sock.accept()
        yield Socket(client), addr

    def send(self, buffer):
        while buffer:
            yield system_call.WriteWait(self.sock)
            len = self.sock.send(buffer)
            buffer = buffer[len:]

    def recv(self, maxbytes):
        yield system_call.ReadWait(self.sock)
        yield self.sock.recv(maxbytes)

    def close(self):
        yield self.sock.close()


