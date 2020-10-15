from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtWidgets import QApplication

from my_QMainWindow import TseMainWindow
from my_utils import SerialReader, parse
from my_math import Logic

import threading


def main():

    logic = Logic()

    serial_reader = SerialReader()
    while not serial_reader.isOpen:
        serial_reader.try_open()

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    window = TseMainWindow()

    serial_reader.signals.message.connect(window.update_labels)
    serial_reader.signals.message.connect(window.update_preview_sliders)
    serial_reader.signals.message.connect(logic.update)

    thread = threading.Thread(target=serial_reader.loop)
    thread.start()

    app.exec_()


if __name__ == '__main__':
    main()
