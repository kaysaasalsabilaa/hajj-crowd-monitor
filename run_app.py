import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.main_window import JendelaUtama


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Hajj Crowd Monitor")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Universitas Airlangga")

    jendela = JendelaUtama()
    jendela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()