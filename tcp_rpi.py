import socket
import sys
import signal

signal.signal(signal.SIGINT, signal.default_int_handler)
from PySide2.QtCore import *


class TCPSignals(QObject):
    message_camera = Signal(str)
    message_imu = Signal(list)


class TCP_Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PORT = 20000
    # server_address = ('192.168.0.220', PORT)
    # server_address = ('192.168.31.162', PORT)
    server_address = ('10.42.0.1', PORT)
    status = 'init'
    client_address = None
    connection = None
    signals = TCPSignals()

    def __init__(self):
        print(f'starting up {self.server_address}')
        try:
            self.sock.bind(self.server_address)
            self.sock.listen(1)
            self.status = 'wait_1_client'
        except:
            print("cannot init TCP server")

    def __del__(self):
        self.status = 'end'
        if self.connection is not None:
            self.connection.close()

    def catch_client(self):
        # Wait for a connection
        if self.status == "wait_1_client":
            print('waiting for a connection')
            self.connection, self.client_address = self.sock.accept()
            self.status = 'receive'

    def loop(self):
        # Receive the data in small chunks and retransmit it
        while self.status != 'end':
            try:
                data = self.connection.recv(64)
                # print(f'received {data}')

                if data:
                    # print(data)
                    if b'imu' in data:
                        message = str(data)
                        start = message.find('imu')
                        end = message.find('end')
                        message = message[start + 3:end].split(";")
                        if len(message) > 2:
                            print(message)
                            self.signals.message_imu.emit(message)
                    else:
                        self.signals.message_camera.emit(str(data))
                    pass
                else:
                    print(f'no more data from {self.client_address}')
            except KeyboardInterrupt:
                self.status = 'end'

    def stop(self):
        self.status = 'end'

# serv = TCP_Server()
# serv.catch_client()
# serv.loop()
