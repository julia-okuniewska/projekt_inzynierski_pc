from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader


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

        self.actuator_names = {
            0: "R2",
            1: "R1",
            2: "G2",
            3: "G1",
            4: "B2",
            5: "B1"
        }

    # def update_preview_sliders(self, messages):



