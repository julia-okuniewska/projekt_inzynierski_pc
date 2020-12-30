import serial
from datetime import datetime
from PySide2.QtCore import *
from PySide2.QtWidgets import QFileDialog


def parse(message):
    message = str(message)
    start = message.find('ac')
    end = message.find('aed')
    return message[start+2:end].replace(r'\r\n', '').replace('\'', '').split(";")


def parse_imu(message):
    message = str(message)
    start = message.find('imu')
    end = message.find('end')
    return message[start+3:end].replace(r'\r\n', '').replace('\'', '').split(";")


class SerialSignals(QObject):
    message = Signal(bytes)


class SerialReader:
    def __init__(self):
        self.ser = serial.Serial()
        self.port_list = ["/dev/ttyACM0", "/dev/ttyUSB0"]
        self.port_iter = 0
        self.ser.port = self.port_list[self.port_iter]
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
            self.port_iter = 1 - self.port_iter
            self.ser.port = self.port_list[self.port_iter]
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
                if b'ac' not in message and b'TASK' not in message and b'PAST' not in message:
                    print(message)

                self.signals.message.emit(message)

    def stop(self):
        self.keep_working = False


class MeasurementLogger:
    def __init__(self):
        self.time = 0
        self.file_handler = 0

    def create_file(self):
        name = QFileDialog.getSaveFileName()
        self.file_handler = open(name[0], "w+")
        self.time = datetime.timestamp(datetime.now())

    def write_to_file(self, content: str):
        now = datetime.timestamp(datetime.now())
        d_t = (now - self.time) * 1000
        # get current time, update and save content to file
        self.file_handler.write(f"{d_t} {content}\r\n")
        # print(f"SAVE {self.time} {content}\r\n")

    def close_file(self):
        print("close file")
        self.file_handler.close()
