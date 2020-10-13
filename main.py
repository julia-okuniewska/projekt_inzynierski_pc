from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtWidgets import QApplication

from my_utils import SerialReader
from my_QMainWindow import TseMainWindow


def main():


    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    window = TseMainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
