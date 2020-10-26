from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader

from my_utils import SerialReader, parse
from hardware import Actuator, actuator_names


class TseMainWindowSignals(QObject):
    sendSerial = Signal(str)


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
        self.ui.group_homing.setEnabled(False)

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
            self.a_mod[i].setText(vals[3])

    def update_preview_sliders(self, vals):
        try:
            i = int(vals[0])
            self.preview_sliders[i].setValue(float(vals[1]))
        except:
            pass

    def prepare_message(self):
        message = self.ui.txt_homing.toPlainText()
        print(message)
        self.signals.sendSerial.emit(message)

