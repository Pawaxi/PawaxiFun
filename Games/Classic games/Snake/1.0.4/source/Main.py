from sys import argv
from PyQt5.QtWidgets import QApplication
from Ui import GameInterface
app = QApplication(argv)
main = GameInterface(None)
main.show()
app.exec()
