import serial


class SerialReader:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyACM0"
        self.ser.baudrate = 9600

    def try_open(self):
        try:
            self.ser.open()
            print("Serial port is open.")
        except Exception as e:
            print("error open serial port: " + str(e))

    def read(self) -> bytes:
        return self.ser.readline()
