import serial

from PySide2.QtCore import *


def parse(message):
    message = str(message)
    start = message.find('ac')
    end = message.find('aed')
    return message[start+2:end].replace(r'\r\n', '').replace('\'', '').split(";")


class SerialSignals(QObject):
    message = Signal(bytes)


class SerialReader:
    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 500000
        # self.ser.baudrate = 9600
        self.isOpen = False
        self.signals = SerialSignals()
        self.keep_working = True

    def __del__(self):
        self.ser.close()

    def try_open(self):
        try:
            self.ser.open()
            self.isOpen = True
            print("Serial port is open.")
        except Exception as e:
            print("error open serial port: " + str(e))

    def read(self) -> bytes:
        return self.ser.readline()

    def write(self, message):
        message = message.encode('utf-8')
        self.ser.write(message)

    def loop(self):
        while self.keep_working:
            if self.ser.in_waiting:
                message = self.read()
                # print(message)
                self.signals.message.emit(message)

    def stop(self):
        self.keep_working = False
