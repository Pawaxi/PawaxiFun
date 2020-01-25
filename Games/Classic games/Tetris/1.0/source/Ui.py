from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox
from PyQt5.QtGui import QColor, QPainter, QFont, QIcon
from PyQt5.QtCore import QTimer, Qt
from Core import Matrix, Vector, Blocks
import Resource
Version = "1.0"
BlockSize = 40
BlankWidth = 200
ScreenSize = Matrix.size.x * BlockSize, Matrix.deathLine * BlockSize
UiSize = ScreenSize[0] + BlankWidth, ScreenSize[1]
BlockColors = {Blocks.Empty:QColor(0, 0, 0),
               Blocks.Z:QColor(255, 255, 0),
               Blocks.S:QColor(0, 255, 255),
               Blocks.I:QColor(255, 0, 255),
               Blocks.L:QColor(100, 155, 255),
               Blocks.J:QColor(155, 100, 255),
               Blocks.O:QColor(255, 155, 100),
               Blocks.T:QColor(0, 0, 255)}
GameRule = """
四格方块（Tetromino）从上往下降落，左右键移动，下键加快降落速度；
A键和D键分别是逆时针和顺时针旋转；
当一行完全被占满时会被消除并且会根据所消去的行数量增加分数。
"""
ProgrammeInfo = """
作者：Happy Hu
版本：%s
更新信息：本版本是首个发布版本。
介绍：本程序是板和羲开源工作室的Pawaxi Fun系列经典游戏之一的俄罗斯方块，将会在各个版本中更新。
"""%Version
class Ui(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.initUi()
        self.initGame()
    def initGame(self):
        self.matrix = Matrix()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGame)
        self.timer.setInterval(1000)
        self.grabKeyboard()#抢夺键盘事件
    def initUi(self):
        self.setFixedSize(*UiSize)
        self.setWindowTitle("Tetris-%s"%Version)
        self.setWindowIcon(QIcon(":/icon"))
        self.startButton = QPushButton('开始游戏', self)
        self.startButton.setGeometry(ScreenSize[0], ScreenSize[1] - 50, BlankWidth, 50)
        self.startButton.clicked.connect(self.startGame)
        self.ruleButton = QPushButton('游戏规则', self)
        self.ruleButton.setGeometry(ScreenSize[0], ScreenSize[1] - 100, BlankWidth, 50)
        self.ruleButton.clicked.connect(lambda:QMessageBox.information(self, '游戏规则', GameRule))
        self.infoButton = QPushButton('程序信息', self)
        self.infoButton.setGeometry(ScreenSize[0], ScreenSize[1] - 150, BlankWidth, 50)
        self.infoButton.clicked.connect(lambda:QMessageBox.information(self, '程序信息', ProgrammeInfo))
    def updateGame(self):
        state = self.matrix.update()
        if state:
            self.timer.stop()
            self.startButton.setDisabled(False)
        self.update()
    def keyPressEvent(self, event):
        self.matrix.keyEvent(event.key())
        self.update()
    def startGame(self):
        self.matrix.restart()
        self.timer.start()
        self.startButton.setDisabled(True)
        self.startButton.setText("再玩一局")
    def paintEvent(self, event):
        pos = Vector()
        qp = QPainter()
        qp.begin(self)
        for pos.x in range(self.matrix.size.x):
            for pos.y in range(self.matrix.deathLine):
                self.paintBlock(qp, pos, self.matrix[pos])
        for pos in self.matrix.tetromino.blockPos():
            self.paintBlock(qp, pos, self.matrix.tetromino.minoType)
        if self.matrix.gameOver:
            qp.setPen(QColor(255, 0, 0))
            qp.setFont(QFont("Times", 60, QFont.Bold))
            qp.drawText(0, 0, ScreenSize[0], ScreenSize[1], Qt.AlignCenter, "GAME OVER")
        qp.setPen(QColor(0, 0, 0))
        qp.setFont(QFont("Times", 25))
        qp.drawText(ScreenSize[0], 0, BlankWidth, 50, Qt.AlignCenter, "分数：%s"%self.matrix.score)
        qp.end()
    def paintBlock(self, qp, pos, block):
        spos = (pos.x * BlockSize, UiSize[1] - (pos.y + 1) * BlockSize)
        qp.setBrush(BlockColors[block])
        qp.drawRect(spos[0], spos[1], BlockSize, BlockSize)
