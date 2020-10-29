actuator_names = {
    0: "R2",        #SA_1
    1: "R1",        #SB_1
    2: "G2",        #SA_2
    3: "G1",        #SB_2
    4: "B2",        #SA_3
    5: "B1"         #SB_3
}


class Actuator:
    def __init__(self, index):
        self.index = index
        self.prev_pos = -1
        self.curr_pos = -1
        self.speed = -1
        self.mode = -1

    def update(self, message):
        if self.prev_pos == -1:
            self.prev_pos = float(message[1])
        else:
            self.prev_pos = self.curr_pos

        self.curr_pos = float(message[1])
        self.speed = int(message[2])
        self.mode = int(message[3])
            # print(f'{self.pos}, {self.speed}, {self.mode}')


class Apex:
    def __init__(self, index):
        self.index = index

        self.x = 0
        self.y = 0
        self.z = 0

    def get_xyz(self):
        return [self.x, self.y, self.z]





