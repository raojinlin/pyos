#!/usr/bin/env python3

import time
import socket

from pyos import system_call
from pyos import socket_wrapper
from pyos import schedule


class TcpServer(object):
    def __init__(self, host='127.0.0.1', port=4444):
        self.host = host
        self.port = port
        
    def start(self):
        print("Server starting on port:", self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

        sock = socket_wrapper.Socket(self.sock)
        while True:
            client, addr = yield sock.accept()
            yield system_call.NewTask(self.handle_client(client, addr))

    @staticmethod
    def handle_client(client, addr):
        print("Connection from", addr)

        host, port = addr
        while True:
            data = yield client.recv(65536)
            if not data:
                break

            message = '%s [%s:%d]: %s' % (time.strftime("%F %H:%M:%S"), host, port, data.decode('utf-8'))
            yield client.send(data.encode('utf-8'))

        client.close()

        print("Client closed")
        yield


def main():
    tcpServer = TcpServer()
    sched = schedule.Scheduler()
    sched.new(tcpServer.start())
    sched.mainloop()


if __name__ == '__main__':
    main()
