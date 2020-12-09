from PySide2.QtCore import QCoreApplication, Qt, QThread
from PySide2.QtWidgets import QApplication

from my_QMainWindow import TseMainWindow
from my_utils import SerialReader
from my_math import *
from tcp_rpi import TCP_Server

import threading


def main():

    logic = Logic()

    # Serial to Arduino
    serial_reader = SerialReader("/dev/ttyUSB0")
    # serial_reader = SerialReader("/dev/ttyACM0")
    while not serial_reader.isOpen:
        serial_reader.try_open()

    # TCP Server to rPi
    tcp_server = TCP_Server()
    tcp_server.catch_client()

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

    # tcp camera message -> gui update
    tcp_server.signals.message.connect(window.update_camera_target_info)

    # logic to dx dy ... predictions
    tcp_server.signals.message.connect(logic.get_dposorient_to_follow_target)
    logic.signals.setFollowedUserSliders.connect(window.update_target_follow_derivatives)

    # timers interruptions, send task to TSE when enable
    window.send_task_timer.timeout.connect(window.prepare_message_task)

    # handle test pos button and set slider to zero button
    window.ui.btn_autosend.clicked.connect(window.send_task_timer_callback)

    window.ui.btn_test_pos.clicked.connect(window.set_sliders_to_test)
    window.ui.btn_zero.clicked.connect(window.set_d_sliders_to_zero)

    # loop button callback
    window.ui.btn_loop.clicked.connect(window.loop_button_callback)

    #threading Serial and TCP
    thread = threading.Thread(target=serial_reader.loop, daemon=True)
    thread.start()

    thread2 = threading.Thread(target=tcp_server.loop, daemon=True)
    thread2.start()

    app.aboutToQuit.connect(lambda: serial_reader.stop())
    app.aboutToQuit.connect(lambda: tcp_server.stop())
    app.exec_()




if __name__ == '__main__':
    main()


