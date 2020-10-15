from hardware import Actuator
from my_utils import parse

class Logic:
    def __init__(self):
        self.actuators = []

        for i in range(6):
            self.actuators.append(Actuator(i))

    def update(self, vals):
        vals = parse(vals)
        i = int(vals[0])
        self.actuators[i].update(vals)