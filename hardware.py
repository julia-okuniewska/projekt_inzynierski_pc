actuator_names = {
    0: "R2",
    1: "R1",
    2: "G2",
    3: "G1",
    4: "B2",
    5: "B1"
}


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
        # print(f'{self.pos}, {self.speed}, {self.mode}')


