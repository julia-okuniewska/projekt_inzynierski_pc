from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader

from my_utils import SerialReader, parse
import numpy as np


class TseMainWindowSignals(QObject):
    sendSerial = Signal(str)
    sliderPosOrient = Signal(list)


class TseMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.signals = TseMainWindowSignals()

        # Load UI and show
        designer_file = QFile("TSE_PC.ui")
        designer_file.open(QFile.ReadOnly)
        loader = QUiLoader()

        self.ui = loader.load(designer_file)
        designer_file.close()

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.ui)
        self.ui.setLayout(grid_layout)

        self.ui.show()
        # -----------------
        self.ui.group_homing.setEnabled(True)

        # -----------------

        self.preview_sliders = {
            0: self.ui.slider_r2,
            1: self.ui.slider_r1,
            2: self.ui.slider_g2,
            3: self.ui.slider_g1,
            4: self.ui.slider_b2,
            5: self.ui.slider_b1
        }

        self.user_sliders = {
            0: self.ui.slider_r2_usr,
            1: self.ui.slider_r1_usr,
            2: self.ui.slider_g2_usr,
            3: self.ui.slider_g1_usr,
            4: self.ui.slider_b2_usr,
            5: self.ui.slider_b1_usr
        }

        self.a_pos = {
            0: self.ui.l_r2_pos,
            1: self.ui.l_r1_pos,
            2: self.ui.l_g2_pos,
            3: self.ui.l_g1_pos,
            4: self.ui.l_b2_pos,
            5: self.ui.l_b1_pos
        }
        self.a_speed = {
            0: self.ui.l_r2_speed,
            1: self.ui.l_r1_speed,
            2: self.ui.l_g2_speed,
            3: self.ui.l_g1_speed,
            4: self.ui.l_b2_speed,
            5: self.ui.l_b1_speed
        }
        self.a_mod = {
            0: self.ui.l_r2_mod,
            1: self.ui.l_r1_mod,
            2: self.ui.l_g2_mod,
            3: self.ui.l_g1_mod,
            4: self.ui.l_b2_mod,
            5: self.ui.l_b1_mod
        }

        self.a_mod_meaning = {
            0: "init",
            1: "stay",
            2: "homing",
            3: "homed",
            4: "centering",
            5: "moving"
        }

        self.current_posorient = {
            0: self.ui.l_top_posorient,
            1: self.ui.l_C1_posorient,
            2: self.ui.l_C2_posorient,
            3: self.ui.l_C3_posorient,
        }
        self.wanted_posorient = {
            0: self.ui.l_top_posorient_2,
            1: self.ui.l_C1_posorient_2,
            2: self.ui.l_C2_posorient_2,
            3: self.ui.l_C3_posorient_2,
        }

        self.pos_orient_slider_message()
        self.ui.slider_dx.valueChanged.connect(self.pos_orient_slider_message)
        self.ui.slider_dy.valueChanged.connect(self.pos_orient_slider_message)
        self.ui.slider_dz.valueChanged.connect(self.pos_orient_slider_message)

        self.ui.slider_d_phi.valueChanged.connect(self.pos_orient_slider_message)
        self.ui.slider_d_theta.valueChanged.connect(self.pos_orient_slider_message)
        self.ui.slider_d_psi.valueChanged.connect(self.pos_orient_slider_message)

    def pos_orient_slider_message(self):
        """predefined by user changes to dx dy dz ..."""
        temp = np.zeros(6)

        temp[0] = self.ui.slider_dx.value()
        temp[1] = self.ui.slider_dy.value()
        temp[2] = self.ui.slider_dz.value()
        temp[3] = self.ui.slider_d_phi.value()
        temp[4] = self.ui.slider_d_theta.value()
        temp[5] = self.ui.slider_d_psi.value()

        temp = temp / 100

        self.ui.l_dx.setText(str(temp[0]))
        self.ui.l_dy.setText(str(temp[1]))
        self.ui.l_dz.setText(str(temp[2]))
        self.ui.l_d_phi.setText(str(temp[3]))
        self.ui.l_d_theta.setText(str(temp[4]))
        self.ui.l_d_psi.setText(str(temp[5]))

        self.signals.sliderPosOrient.emit(list(temp))

    def parse_incoming_message(self, message):
        if message == b"ALL_HOME\r\n":
            self.ui.group_homing.setEnabled(True)
        else:
            message = parse(message)
            self.update_labels(message)
            self.update_preview_sliders(message)

    def update_labels(self, vals):
        if len(vals) == 4:
            i = int(vals[0])
            self.a_pos[i].setText(vals[1])
            self.a_speed[i].setText(vals[2])
            self.a_mod[i].setText(self.a_mod_meaning[int(vals[3])])

    def update_preview_sliders(self, vals):
        try:
            i = int(vals[0])
            self.preview_sliders[i].setValue(float(vals[1]))
        except:
            pass

    def update_user_sliders(self, vals):
        for i in self.user_sliders:
            self.user_sliders[i].setValue(vals[i])

    def update_current_posorient(self, vals_top, vals_c1, vals_c2, vals_c3):
        def prepare_string(arr):
            arr = np.around(arr, decimals=3)
            return f"{arr[0]}   {arr[1]}    {arr[2]}    {arr[3]}    {arr[4]}    {arr[5]}"

        def prepare_string2(arr):
            arr = np.around(arr, decimals=3)
            return f"{arr[0]}   {arr[1]}    {arr[2]}"

        self.current_posorient[0].setText(prepare_string(vals_top))
        self.current_posorient[1].setText(prepare_string2(vals_c1))
        self.current_posorient[2].setText(prepare_string2(vals_c2))
        self.current_posorient[3].setText(prepare_string2(vals_c3))

    def prepare_message_homing(self):
        message = self.ui.txt_homing.toPlainText()
        self.signals.sendSerial.emit(message)

    def prepare_message_task(self):
        vals = np.zeros((6,))
        for i in self.user_sliders:
            vals[i] = self.user_sliders[i].value()

        vals = np.around(vals, decimals=0)
        vals = [int(v) for v in vals]
        # print(vals)

        message = f"tsk{vals[0]};{vals[1]};{vals[2]};{vals[3]};{vals[4]};{vals[5]}end"
        # print(message)

        self.signals.sendSerial.emit(message)

