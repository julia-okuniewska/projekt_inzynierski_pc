from hardware import Actuator, Apex
from my_utils import parse
import numpy as np


class Logic:
    def __init__(self):
        self.actuators = []
        self.apexes = []        # C1, C2, C3

        self.upper_plate_pos = [0, 0, 0]
        self.upper_plate_orient = [0, 0, 0]

        for i in range(6):
            self.actuators.append(Actuator(i))

        for i in range(3):
            self.apexes.append(Apex(i))

    def update(self, vals):
        try:
            vals = parse(vals)
            i = int(vals[0])
            self.actuators[i].update(vals)
        except:
            pass

    def get_p(self):
        return [*self.upper_plate_pos, *self.upper_plate_orient]

    def get_q(self):
        q = [act.curr_pos - act.prev_pos for act in self.actuators]
        return q


    def when_all_available(self):

        print("df")


logic = Logic()
print(logic.get_p())

def calculate_JC(tse_pos, tse_orient):
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
                       [     -l_t*0.5*r*cos_f,       l_t*0.5*cos_t,                                   0]])

    JC_3 = np.asarray([[                     0, l_t*0.5*sin_t*cos_p, l_t*(0.5*cos_t*sin_p - 0.5*r*cos_p)],
                       [-l_t*0.5*r*sin_f*cos_p,                   0,  -l_t*(0.5*cos_p+0.5*r*cos_f*sin_p)],
                       [       l_t*0.5*r*cos_f,       l_t*0.5*cos_t,                                   0]])

    # JC = [rotz(-90) * eye(3), rotz(-90) * JC_1;
    # rotz(30) * eye(3), rotz(30) * JC_2;
    # rotz(150) * eye(3), rotz(150) * JC_3];
    # % JC = [eye(3), JC_1;
    # eye(3), JC_2;
    # eye(3), JC_3];


def calculate_JS_partial(sa, sb, apex):
    L_0 = 0.557036
    L_1 = 0.476
    L = L_0 + 2 * L_1

    r = np.sqrt(3)
    m = (1/4)*(1 - (L/L_0)**2)

    x = apex[0]
    y = apex[1]
    z = apex[2]

    JS = np.zeros((2, 3))

    JSP_11 = (-m * r * (sa + sb) * (sa + 2 * sb) + (r * sa - 2 * x) * (r * x + 2 * sb - y)) / (
                m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                    2 * m * sa + m * sb + r * x - 2 * sa + y))
    JSP_12 = (-m * (sa - sb) * (sa + 2 * sb) + (sa - 2 * y) * (r * x + 2 * sb - y)) / (
                m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                    2 * m * sa + m * sb + r * x - 2 * sa + y))
    JSP_13 = -2 * z * (r * x + 2 * sb - y) / (m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                2 * m * sa + m * sb + r * x - 2 * sa + y))
    JSP_21 = (r * (sa + sb) * (2 * m * sa + m * sb + r * x - 2 * sa + y) - (r * sa - 2 * x) * (r * x - 2 * sa + y)) / (
                m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                    2 * m * sa + m * sb + r * x - 2 * sa + y))
    JSP_22 = ((sa - sb) * (2 * m * sa + m * sb + r * x - 2 * sa + y) - (sa - 2 * y) * (r * x - 2 * sa + y)) / (
                m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                    2 * m * sa + m * sb + r * x - 2 * sa + y))
    JSP_23 = 2 * z * (r * x - 2 * sa + y) / (m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                2 * m * sa + m * sb + r * x - 2 * sa + y))

    JS[0, 0] = JSP_11
    JS[0, 1] = JSP_12
    JS[0, 2] = JSP_13

    JS[1, 0] = JSP_21
    JS[1, 1] = JSP_22
    JS[1, 2] = JSP_23

    return JS


def calculate_JS(sa_1, sb_1, sa_2, sb_2, sa_3, sb_3, apex_1, apex_2, apex_3):
    L_0 = 0.557036
    L_1 = 0.476
    L = L_0 + 2 * L_1

    r = np.sqrt(3)
    m = (1 / 4) * (1 - (L / L_0) ** 2)

    p_sa = [sa_1, sa_2, sa_3]
    p_sb = [sb_1, sb_2, sb_3]
    p_x = [apex_1[0], apex_2[0], apex_3[0]]
    p_y = [apex_1[1], apex_2[1], apex_3[1]]
    p_z = [apex_1[2], apex_2[2], apex_3[2]]

    JS = np.zeros((6, 9))

    for i in range(3):
        sa = p_sa[i]
        sb = p_sb[i]

        x = p_x[i]
        y = p_y[i]
        z = p_z[i]

        JSP_11 = (-m * r * (sa + sb) * (sa + 2 * sb) + (r * sa - 2 * x) * (r * x + 2 * sb - y)) / (
                    m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                        2 * m * sa + m * sb + r * x - 2 * sa + y))
        JSP_12 = (-m * (sa - sb) * (sa + 2 * sb) + (sa - 2 * y) * (r * x + 2 * sb - y)) / (
                    m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                        2 * m * sa + m * sb + r * x - 2 * sa + y))
        JSP_13 = -2 * z * (r * x + 2 * sb - y) / (m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                    2 * m * sa + m * sb + r * x - 2 * sa + y))
        JSP_21 = (r * (sa + sb) * (2 * m * sa + m * sb + r * x - 2 * sa + y) - (r * sa - 2 * x) * (r * x - 2 * sa + y)) / (
                    m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                        2 * m * sa + m * sb + r * x - 2 * sa + y))
        JSP_22 = ((sa - sb) * (2 * m * sa + m * sb + r * x - 2 * sa + y) - (sa - 2 * y) * (r * x - 2 * sa + y)) / (
                    m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                        2 * m * sa + m * sb + r * x - 2 * sa + y))
        JSP_23 = 2 * z * (r * x - 2 * sa + y) / (m * (sa + 2 * sb) * (r * x - 2 * sa + y) - (r * x + 2 * sb - y) * (
                    2 * m * sa + m * sb + r * x - 2 * sa + y))

        i_x = i * 2
        i_y = i * 3

        JS[i_x, i_y] = JSP_11
        JS[i_x, i_y + 1] = JSP_12
        JS[i_x, i_y + 2] = JSP_13
        JS[i_x + 1, i_y] = JSP_21
        JS[i_x + 1, i_y + 1] = JSP_22
        JS[i_x + 1, i_y + 2] = JSP_23

    return JS

calculate_JS(1, 2, 3, 4, 5, 6, [1, 2, 3], [1, 2, 3], [1, 2, 3])