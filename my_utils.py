import serial

from PySide2.QtCore import *
from PySide2.QtGui import *


def parse(message):
    message = str(message)
    start = message.find('ac')
    return message[start+2:].replace(r'\r\n', '').replace('\'', '').split(";")


class SerialSignals(QObject):
    message = Signal(bytes)


class SerialReader:
    def __init__(self):
        self.ser = serial.Serial()
        # self.ser.port = "/dev/ttyUSB0"
        self.ser.port = "/dev/ttyACM0"
        self.ser.baudrate = 9600
        self.isOpen = False
        self.signals = SerialSignals()

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
        while True:
            message = self.read()
            print(message)
            self.signals.message.emit(message)


