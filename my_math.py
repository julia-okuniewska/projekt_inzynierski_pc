from hardware import Actuator
from my_utils import parse
import numpy as np

class Logic:
    def __init__(self):
        self.actuators = []

        for i in range(6):
            self.actuators.append(Actuator(i))

    def update(self, vals):
        try:
            vals = parse(vals)
            i = int(vals[0])
            self.actuators[i].update(vals)
        except:
            pass

def calc_JS_partial():
    L_0 = 0.557036 # Length of first arm link
    L_1 = 0.476
    L = L_0 + 2 * L_1

    r = np.sqrt(3)
    m = (1/4)*(1 - (L/L_0)**2)


def cal_JC(tse_pos, tse_orient):
    r = np.sqrt(3)
    l_t = 0.3498745 # center upper platform to apex

    f = tse_orient[0]  # phi
    t = tse_orient[1]  # theta
    p = tse_orient[2]  # psi

    sin_f = np.sin(f)
    sin_t = np.sin(t)
    sin_p = np.sin(p)

    cos_f = np.cos(f)
    cos_t = np.cos(t)
    cos_p = np.cos(p)

    JC_1 = np.asarray([[0, -l_t*sin_t*cos_p, -l_t*cos_t*sin_p],
                       [0,                0,        l_t*cos_p],
                       [0,       -l_t*cos_t,                0]])

    JC_2 = np.asarray([[                    0, l_t*0.5*sin_t*cos_p, l_t*(0.5*cos_t*sin_p + 0.5*r*cos_p)],
                       [l_t*0.5*r*sin_f*cos_p,                   0,    -l_t*(0.5*cos_p-0.5*cos_f*sin_p)],
                       [      -l_t*0.5*r*cos_f,      l_t*0.5*cos_t,                                  0]])

    JC_3 = np.asarray([[                     0, l_t*0.5*sin_t*cos_p, l_t*(0.5*cos_t*sin_p - 0.5*r*cos_p)],
                       [-l_t*0.5*r*sin_f*cos_p,                   0,  -l_t*(0.5*cos_p+0.5*r*cos_f*sin_p)],
                       [       l_t*0.5*r*cos_f,       l_t*0.5*cos_t,                                   0]])

    # JC = [rotz(-90) * eye(3), rotz(-90) * JC_1;
    # rotz(30) * eye(3), rotz(30) * JC_2;
    # rotz(150) * eye(3), rotz(150) * JC_3];
    # % JC = [eye(3), JC_1;
    # eye(3), JC_2;
    # eye(3), JC_3];