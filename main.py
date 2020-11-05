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

    serial_reader.signals.message.connect(window.parse_incoming_message)
    serial_reader.signals.message.connect(logic.update)

    window.ui.btn_homing.clicked.connect(window.prepare_message_homing)
    window.signals.sendSerial.connect(serial_reader.write)

    window.signals.sliderPosOrient.connect(logic.slider_pos_orient)
    logic.signals.setUserSliderValues.connect(window.update_user_sliders)

    logic.signals.setCurrentPosOrient.connect(window.update_current_posorient)

    window.ui.btn_task.clicked.connect(window.prepare_message_task)

    thread = threading.Thread(target=serial_reader.loop)
    thread.start()

    app.aboutToQuit.connect(lambda: serial_reader.stop())
    app.exec_()


if __name__ == '__main__':
    main()
