from PySide2.QtCore import QCoreApplication, Qt, QThread
from PySide2.QtWidgets import QApplication

from my_QMainWindow import TseMainWindow
from my_utils import SerialReader
from my_math import *

import threading


def main():

    logic = Logic()

    serial_reader = SerialReader()
    while not serial_reader.isOpen:
        serial_reader.try_open()

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    window = TseMainWindow()

    # logika
    serial_reader.signals.message.connect(window.parse_incoming_message)
    serial_reader.signals.message.connect(logic.update)

    # przyciski HOME
    window.ui.btn_homing.clicked.connect(window.prepare_message_homing)
    window.signals.sendSerial.connect(serial_reader.write)

    # from GUI dx dy to cal logic
    window.signals.sliderPosOrient.connect(logic.slider_pos_orient)
    # from logic to update sliders with wanted pos
    logic.signals.setUserSliderValues.connect(window.update_user_sliders)

    # apexes from logic to gui update
    logic.signals.setCurrentPosOrient.connect(window.update_current_posorient)
    logic.signals.setWantedPosOrient.connect(window.update_wanted_posorient)

    # task sending
    window.ui.btn_task.clicked.connect(window.prepare_message_task)

    thread = threading.Thread(target=serial_reader.loop)
    thread.start()

    app.aboutToQuit.connect(lambda: serial_reader.stop())
    app.exec_()


if __name__ == '__main__':
    main()
