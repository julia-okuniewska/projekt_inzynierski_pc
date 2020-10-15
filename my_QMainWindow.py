from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader

from my_utils import SerialReader, parse
from hardware import Actuator



class TseMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

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

        self.actuator_names = {
            0: "R2",
            1: "R1",
            2: "G2",
            3: "G1",
            4: "B2",
            5: "B1"
        }

    def update_labels(self, vals):
        vals = parse(vals)
        i = int(vals[0])
        self.a_pos[i].setText(vals[1])
        self.a_speed[i].setText(vals[2])
        self.a_mod[i].setText(vals[3])

    def update_preview_sliders(self, vals):
        vals = parse(vals)
        i = int(vals[0])
        self.preview_sliders[i].setValue(float(vals[1]))



