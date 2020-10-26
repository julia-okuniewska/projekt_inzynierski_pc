from hardware import Actuator, Apex
from my_utils import parse
import numpy as np


class Logic:
    def __init__(self):
        self.actuators = []
        self.apexes = []  # C1, C2, C3

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


def calculate_JC(tse_pos, tse_orient):
    r = np.sqrt(3)
    l_t = 0.3498745  # center upper platform to apex

    f = tse_orient[0]  # phi
    t = tse_orient[1]  # theta
    p = tse_orient[2]  # psi

    sin_f, sin_t, sin_p = np.sin(f), np.sin(t), np.sin(p)
    cos_f, cos_t, cos_p = np.cos(f), np.cos(t), np.cos(p)

    JC_1 = np.asarray([[0, -l_t * sin_t * cos_p, -l_t * cos_t * sin_p],
                       [0, 0, l_t * cos_p],
                       [0, -l_t * cos_t, 0]])

    JC_2 = np.asarray([[0, l_t * 0.5 * sin_t * cos_p, l_t * (0.5 * cos_t * sin_p + 0.5 * r * cos_p)],
                       [l_t * 0.5 * r * sin_f * cos_p, 0, -l_t * (0.5 * cos_p - 0.5 * r * cos_f * sin_p)],
                       [-l_t * 0.5 * r * cos_f, l_t * 0.5 * cos_t, 0]])

    JC_3 = np.asarray([[0, l_t * 0.5 * sin_t * cos_p, l_t * (0.5 * cos_t * sin_p - 0.5 * r * cos_p)],
                       [-l_t * 0.5 * r * sin_f * cos_p, 0, -l_t * (0.5 * cos_p + 0.5 * r * cos_f * sin_p)],
                       [l_t * 0.5 * r * cos_f, l_t * 0.5 * cos_t, 0]])

    def rotz(angle):
        angle = np.radians(angle)
        sin_a, cos_a = np.sin(angle), np.cos(angle)
        rot = np.asarray([[cos_a, -sin_a, 0],
                          [sin_a, cos_a, 0],
                          [0, 0, 1]])

        return np.around(rot, decimals=3)

    JC = np.zeros((9, 6))

    JC[0:3, 0:3] = rotz(-90) @ np.eye(3)
    JC[0:3, 3:6] = rotz(-90) @ JC_1

    JC[3:6, 0:3] = rotz(30) @ np.eye(3)
    JC[3:6, 3:6] = rotz(30) @ JC_2

    JC[6:9, 0:3] = rotz(150) @ np.eye(3)
    JC[6:9, 3:6] = rotz(150) @ JC_3

    return JC


def calculate_JS_partial(sa, sb, apex):
    L_0 = 0.557036
    L_1 = 0.476
    L = L_0 + 2 * L_1

    r = np.sqrt(3)
    m = (1 / 4) * (1 - (L / L_0) ** 2)

    x, y, z = apex[0], apex[1], apex[2]
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
        sa, sb = p_sa[i], p_sb[i]
        x, y, z = p_x[i], p_y[i], p_z[i]

        JSP = calculate_JS_partial(sa, sb, [x, y, z])

        i_x, i_y = i * 2, i * 3
        JS[i_x:i_x + 2, i_y:i_y + 3] = JSP

    return JS
