class Actuator:
    def __init__(self, index):
        self.index = index
        self.pos = -1
        self.speed = -1
        self.mode = -1

    def update(self, message):
        self.pos = float(message[1])
        self.speed = int(message[2])
        self.mode = int(message[3])
        print(f'{self.pos}, {self.speed}, {self.mode}')


