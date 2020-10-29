from PySide2.QtCore import QObject, Signal

from hardware import Actuator, Apex
from my_utils import parse
import numpy as np


def rotx(angle):
    angle = np.radians(angle)
    sin_a, cos_a = np.sin(angle), np.cos(angle)
    rot = np.asarray([[1,     0,      0],
                      [0, cos_a, -sin_a],
                      [0, sin_a,  cos_a]])

    return np.around(rot, decimals=3)


def roty(angle):
    angle = np.radians(angle)
    sin_a, cos_a = np.sin(angle), np.cos(angle)
    rot = np.asarray([[ cos_a,   0, sin_a],
                      [     0,   1,     0],
                      [-sin_a,   0, cos_a]])

    return np.around(rot, decimals=3)


def rotz(angle):
    angle = np.radians(angle)
    sin_a, cos_a = np.sin(angle), np.cos(angle)
    rot = np.asarray([[cos_a,  -sin_a, 0],
                      [sin_a,   cos_a, 0],
                      [0,           0, 1]])

    return np.around(rot, decimals=3)


class LogicSignals(QObject):
    setUserSliderValues = Signal(list)


class Logic:
    def __init__(self):

        self.signals = LogicSignals()

        self.actuators = []
        self.apexes = []  # C1, C2, C3

        self.upper_plate_pos = [0.01, 0.01, 0.5]
        self.upper_plate_orient = [0.01, 0.01, 0.01]

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
        return np.asarray([*self.upper_plate_pos, *self.upper_plate_orient])

    def get_q(self):
        q = [act.curr_pos - act.prev_pos for act in self.actuators]
        return q

    def get_act_pos(self):
        pos = [act.curr_pos for act in self.actuators]
        return np.asarray(pos)

    def get_apex_points(self, Xt, orient):
        l_t = 0.3498745  # center upper platform to apex
        # (1)
        phi, theta, psi = orient[0], orient[1], orient[2]
        matrix = np. around(rotx(phi) @ roty(theta) @ rotz(psi), decimals=3)

        n = matrix[:, 0]
        t = matrix[:, 1]
        b = matrix[:, 2]

        sqr32 = np.sqrt(3)/2

        apex1 = Xt + l_t * n
        apex2 = Xt + l_t * (sqr32 * t + 0.5 * n)
        apex3 = Xt + l_t * (sqr32 * t - 0.5 * n)

        return apex1, apex2, apex3

    def slider_pos_orient(self, arr):
        # # upper plate pos orient który chcę osiągnąć
        # pos, orient = arr[0:3], arr[3:6]
        #
        # # jc = calculate_JC(pos, orient)
        # apex1, apex2, apex3 = self.get_apex_points(pos, orient)
        #
        # js = calculate_JS(*self.get_q(), apex1, apex2, apex3)
        # ji = js @ jc
        #
        # p_p = self.get_p()
        # p = np.asarray(arr)
        # p = p - p_p
        # p = np.around(p, decimals=2)
        #
        # new_q = ji @ p
        # new_q = new_q * 7500
        #
        # pos = np.asarray(self.get_act_pos())
        # new_q = pos + new_q
        # self.signals.setUserSliderValues.emit(list(new_q))

        # upper plate pos orient który chcę osiągnąć
        pos, orient = arr[0:3], arr[3:6]

        # jc = calculate_JC(pos, orient)
        apex1, apex2, apex3 = self.get_apex_points(pos, orient)

        p_curr = self.get_p()
        pos_curr = p_curr[0:3]
        orient_curr = p_curr[3:6]

        delta_X = np.asarray(pos - pos_curr)
        delta_Theta = np.asarray(orient - orient_curr)

        q = self.get_act_pos()
        q = q / 7500

        js1 = calculate_JS_partial(q[0], q[1], apex1)
        js2 = calculate_JS_partial(q[2], q[3], apex2)
        js3 = calculate_JS_partial(q[4], q[5], apex3)

        jt = np.zeros((6, 3))

        jt[0:2, 0:3] = js1
        jt[2:4, 0:3] = js2
        jt[4:6, 0:3] = js3

        dT = np.asarray([[0,  0,  0],
                         [0,  0,  1],
                         [0, -1,  0]])

        dN = np.asarray([[0,  0, -1],
                         [0,  0,  1],
                         [1,  0,  0]])

        jr = np.zeros((6,3))

        sqr3_2 = np.sqrt(3)/2

        jr[0:2, 0:3] = js1 @ dN
        jr[2:4, 0:3] = -js2 @ (sqr3_2 * dT + 0.5 * dN)
        jr[4:6, 0:3] =  js3 @ (sqr3_2 * dT - 0.5 * dN)

        l_t = 0.3498745  # center upper platform to apex
        jr = l_t * jr

        delta_q = jt @ delta_X + jr @ delta_Theta

        print("delta_q : ", delta_q)

        new_q = (q + delta_q) * 7500

        self.signals.setUserSliderValues.emit(list(new_q))





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


