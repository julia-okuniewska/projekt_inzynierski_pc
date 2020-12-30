from PySide2.QtCore import QObject, Signal

from hardware import Actuator, Apex
from my_utils import parse
import numpy as np
from math import atan2, asin



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

# a = rotz(-90)
# point = np.asarray([0.3, 0, 0.8]).T
# print(point@a)


class LogicSignals(QObject):
    setUserSliderValues = Signal(list)
    setCurrentPosOrient = Signal(list, list, list, list)
    setWantedPosOrient = Signal(list, list, list, list)

    setFollowedUserSliders = Signal(tuple)


class Logic:
    def __init__(self):

        self.signals = LogicSignals()

        self.actuators = []
        self.apexes = []  # C1, C2, C3

        # init values after calibration, midpos
        self.upper_plate_pos = [0.0, 0.0, 0.5]
        self.upper_plate_orient = [0.0, 0.0, 0.0]

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

    def qet_curr_q(self):
        pos = [act.curr_pos for act in self.actuators]
        return np.asarray(pos)

    def get_apex_points(self, Xt, orient):
        l_t = 0.3498745  # center upper platform to apex
        # (1)
        phi, theta, psi = orient[0], orient[1], orient[2]
        matrix = np. around(rotz(psi) @ roty(theta) @ rotx(phi), decimals=3)

        n = matrix[:, 0]
        t = matrix[:, 1]
        b = matrix[:, 2]

        sqr32 = np.sqrt(3)/2

        apex1 = Xt + l_t * n
        apex2 = Xt - l_t * (sqr32 * t + 0.5 * n)
        apex3 = Xt + l_t * (sqr32 * t - 0.5 * n)

        return apex1, apex2, apex3

    def slider_pos_orient(self, arr):

        delta_q = self.method_one(self.get_p(), arr)

        q = np.around(self.qet_curr_q() / 7500, decimals=2)
        q = 1 - q
        new_q = 7500 - (q + delta_q) * 7500

        self.signals.setUserSliderValues.emit(list(new_q))

    def method_one(self, p, delta_p):
        pos, orient = p[0:3], p[3:6]
        jc = calculate_JC(pos, orient)
        apex1, apex2, apex3 = self.get_apex_points(np.asarray(pos), self.upper_plate_orient)

        apex1 = (apex1.T@rotz(-90)).T
        apex2 = (apex2.T@rotz(30)).T
        apex3 = (apex3.T@rotz(150)).T

        q = np.around(self.qet_curr_q() / 7500, decimals=2)
        q = 1 - q

        js = calculate_JS(*q, apex1, apex2, apex3)
        ji = js @ jc

        delta_q = ji @ delta_p

        self.signals.setCurrentPosOrient.emit(self.get_p(), apex1, apex2, apex3)

        new_p = p + delta_p
        pos, orient = new_p[0:3], new_p[3:6]
        apex1_wanted, apex2_wanted, apex3_wanted = self.get_apex_points(np.asarray(pos), self.upper_plate_orient)

        apex1_wanted = (apex1_wanted.T @ rotz(-90)).T
        apex2_wanted = (apex2_wanted.T @ rotz(30)).T
        apex3_wanted = (apex3_wanted.T @ rotz(150)).T

        self.signals.setWantedPosOrient.emit(new_p, apex1_wanted, apex2_wanted, apex3_wanted)
        return delta_q


    def method_two(self, arr):
        # upper plate pos orient który chcę osiągnąć
        target_pos, target_orient = arr[0:3], arr[3:6]

        p_curr = self.get_p()
        curr_pos, curr_orient = p_curr[0:3], p_curr[3:6]

        apex1, apex2, apex3 = self.get_apex_points(target_pos, target_orient)

        delta_X = np.asarray(target_pos - curr_pos)
        delta_Theta = np.asarray(target_orient - curr_orient)

        q = np.around(self.qet_curr_q() / 7500, decimals=2)
        q = 1 - q

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
                         [0,  0,  0],
                         [1,  0,  0]])

        jr = np.zeros((6, 3))

        sqr3_2 = np.sqrt(3)/2

        jr[0:2, 0:3] = js1 @ dN
        jr[2:4, 0:3] = -js2 @ (sqr3_2 * dT + 0.5 * dN)
        jr[4:6, 0:3] =  js3 @ (sqr3_2 * dT - 0.5 * dN)

        # l_t = 0.3498745  # center upper platform to apex
        l_t = 0.1798745  # center upper platform to apex
        jr = l_t * jr

        delta_q = jt @ delta_X + jr @ delta_Theta

        return delta_q

    def get_dposorient_to_follow_target(self, target_data):
        target_data = str(target_data)
        target_data = target_data.replace("b", "").replace("'", "").split(';')

        if len(target_data) == 1 and target_data[0] == "empty":
            pass

        elif len(target_data) == 4:
            # print(target_data)
            dir_width, dir_height, val_width, val_height = target_data
            val_width = int(float(val_width))
            val_height = int(float(val_height))

            if dir_width == 'left':
                d_yaw = - 0.5 * val_width
            elif dir_width == 'right':
                d_yaw =   0.5 * val_width
            else:
                d_yaw = 0

            if dir_height == 'up':
                # d_z =  val_height/100
                d_z =   val_height
            elif dir_height == 'down':
                # d_z = -val_height/100
                d_z = -  val_height

            else:
                d_z = 0
            # print(val_width, val_height, d_yaw, d_z)
        dd = (d_z, d_yaw)
        self.signals.setFollowedUserSliders.emit(dd)


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
    # L_0 = 0.265
    L_1 = 0.476
    # L_1 = 0.22
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

def to_euler(w, x, y, z):
    """
    Returns the Euler angles as a tuple(roll, pitch, yaw)
    This is a modified version of this:
    https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    """
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = atan2(t3, t4)

    X = np.rad2deg(X)
    Y = np.rad2deg(Y)
    Z = np.rad2deg(Z)

    X = np.around(X, decimals=2)
    Y = np.around(Y, decimals=2)
    Z = np.around(Z, decimals=2)

    return X, Y, Z
