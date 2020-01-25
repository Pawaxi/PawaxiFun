from Core import PIXEL_TYPES, System, Vector, DIRECTIONS
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox
from PyQt5.QtGui import QColor, QPainter, QFont, QIcon
from PyQt5.QtCore import QTimer, Qt
import resource
VERSION = "1.0.4"
PIXEL_SIDE_LENGTH = 30#游戏像素边长（对应实际的像素数）
BLANK_WIDTH = 200
MATRIX_SCREEN_SIZE = Vector(System.MATRIX_SIZE.x * PIXEL_SIDE_LENGTH, System.MATRIX_SIZE.y * PIXEL_SIDE_LENGTH)#矩阵实际显示时的像素数
GAME_INTERFACE_SIZE = Vector(MATRIX_SCREEN_SIZE.x + BLANK_WIDTH, MATRIX_SCREEN_SIZE.y)#游戏界面size

PIXEL_COLORS = {PIXEL_TYPES.EMPTY:[QColor(0, 0, 0), QColor(127, 0, 128)],
                PIXEL_TYPES.BARRIER:[QColor(255, 0, 0), QColor(0, 0, 255)],
                PIXEL_TYPES.SNAKE_BODY:[QColor(0, 200, 0), QColor(0, 200, 0)],
                PIXEL_TYPES.FOOD:[QColor(0, 0, 255), QColor(255, 0, 0)],
                PIXEL_TYPES.SNAKE_HEAD:[QColor(0, 255, 0), QColor(0, 255, 0)],
                PIXEL_TYPES.POISON:[QColor(255, 255, 0), QColor(255, 255, 0)]}#游戏像素不同类型的颜色，分别是没中毒和中毒时的颜色
UPDATE_INTERVAL = 210#更新时间间隔
GAME_RULES = """
上下左右键控制蛇的移动方向，绿色部分为蛇身，较亮的格子代表蛇头；
蓝色格子是食物，红色格子是障碍物，黄色格子是毒药；
在每次吃到食物时，蓝色、红色、黄色格子都会更新，请注意；
当碰到障碍物、游戏界面边缘或碰到蛇身时，游戏结束；
如果吃到毒药，将会出现奇特的视觉，并且爬行方向会变得完全相反。
"""
PROGRAMME_INFO = """
作者：Happy Hu
版本：%s
更新信息：本版本是首个发布版本。
介绍：本程序是Pawaxi Fun系列开源程序之一。仿照经典游戏《贪吃蛇》，制作了类似的游戏，新的功能将会在各个版本中陆续加入。
"""%(VERSION)
class GameInterface(QWidget):
    #游戏界面widget
    WIDGET_HEIGHT = 50#子控件的高
    START_BUTTON_GEOMETRY = (GAME_INTERFACE_SIZE.x - BLANK_WIDTH, GAME_INTERFACE_SIZE.y - WIDGET_HEIGHT, BLANK_WIDTH, WIDGET_HEIGHT)
    RULE_BUTTON_GEOMETRY = (GAME_INTERFACE_SIZE.x - BLANK_WIDTH, GAME_INTERFACE_SIZE.y - 2 * WIDGET_HEIGHT, BLANK_WIDTH, WIDGET_HEIGHT)
    INFO_BUTTON_GEOMETRY = (GAME_INTERFACE_SIZE.x - BLANK_WIDTH, GAME_INTERFACE_SIZE.y - 3 * WIDGET_HEIGHT, BLANK_WIDTH, WIDGET_HEIGHT)
    SCORE_GEOMETRY = (MATRIX_SCREEN_SIZE.x, 0, BLANK_WIDTH, WIDGET_HEIGHT)
    POISONED_HINT_GEOMETRY = (MATRIX_SCREEN_SIZE.x, WIDGET_HEIGHT, BLANK_WIDTH, 2 * WIDGET_HEIGHT)
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.initWidgets()
        self.initGameSettings()
    def initWidgets(self):
        self.setFixedSize(GAME_INTERFACE_SIZE.x, GAME_INTERFACE_SIZE.y)
        self.setWindowTitle("Snake-%s"%VERSION)
        self.setWindowIcon(QIcon(":/icon"))
        self.startButton = QPushButton("开始游戏", self)
        self.startButton.setGeometry(*self.START_BUTTON_GEOMETRY)
        self.startButton.clicked.connect(self.startGame)
        self.ruleButton = QPushButton("游戏规则", self)
        self.ruleButton.setGeometry(*self.RULE_BUTTON_GEOMETRY)
        self.ruleButton.clicked.connect(lambda:QMessageBox.information(self, "游戏规则", GAME_RULES))
        self.infoButton = QPushButton("程序信息", self)
        self.infoButton.setGeometry(*self.INFO_BUTTON_GEOMETRY)
        self.infoButton.clicked.connect(lambda:QMessageBox.information(self, "程序信息", PROGRAMME_INFO))
    def initGameSettings(self):
        self.system = System()
        self.timer = QTimer(self)
        self.timer.setInterval(UPDATE_INTERVAL)
        self.timer.timeout.connect(self.updateGame)
        self.paintCursor = Vector()#网格绘制光标
        self.gameOver = False
        self.grabKeyboard()#抢夺键盘事件
        self.gameModeNormal = True#默认游戏模式为标准的
    def updateGame(self):
        #更新游戏实况并重绘
        hint = self.system.update()
        if hint is None:
            self.update()
        else:
            self.timer.stop()
            self.system.stopPoisonTimer()
            self.gameOver = True
            self.startButton.setDisabled(False)
            self.update()
    def paintEvent(self, event):
        #绘制游戏界面和分数
        qp = QPainter()
        qp.begin(self)
        for self.paintCursor.x in range(System.MATRIX_SIZE.x):
            for self.paintCursor.y in range(System.MATRIX_SIZE.y):
                self.drawGamePixel(qp)
        self.drawScore(qp)
        if self.gameOver:
            self.drawGameOverHint(qp)
        elif self.system.directionReversed:#在游戏结束后不会显示
            self.drawPoisonedHint(qp)
        qp.end()
    def drawGamePixel(self, qp):
        qp.setBrush(PIXEL_COLORS[self.system.matrix[self.paintCursor]][int(self.system.directionReversed)])
        qp.drawRect(PIXEL_SIDE_LENGTH * self.paintCursor.x, PIXEL_SIDE_LENGTH * self.paintCursor.y,
                    PIXEL_SIDE_LENGTH, PIXEL_SIDE_LENGTH)
    def drawScore(self, qp):
        qp.setPen(QColor(0, 0, 0))
        qp.setFont(QFont('MicrosoftYahei', 20))
        qp.drawText(self.SCORE_GEOMETRY[0], self.SCORE_GEOMETRY[1], self.SCORE_GEOMETRY[2], self.SCORE_GEOMETRY[3],
                    Qt.AlignCenter, "分数：%s"%self.system.foodScore)
    def drawGameOverHint(self, qp):
        qp.setPen(QColor(255, 0, 0))
        qp.setFont(QFont('MicrosoftYahei', 140, QFont.Bold))
        qp.drawText(0, 0, MATRIX_SCREEN_SIZE.x, MATRIX_SCREEN_SIZE.y,
                    Qt.AlignCenter, "GAME OVER")
    def drawPoisonedHint(self, qp):
        qp.setPen(QColor(255, 0, 0))
        qp.setFont(QFont('MicrosoftYahei', 15))
        qp.drawText(self.POISONED_HINT_GEOMETRY[0], self.POISONED_HINT_GEOMETRY[1],
                    self.POISONED_HINT_GEOMETRY[2], self.POISONED_HINT_GEOMETRY[3],
                    Qt.AlignCenter, "蛇中毒了，\n还剩%s个时间单位\n恢复正常"%self.system.poisonTimer)
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.system.keyEvent(DIRECTIONS.LEFT)
        elif key == Qt.Key_Right:
            self.system.keyEvent(DIRECTIONS.RIGHT)
        elif key == Qt.Key_Up:
            self.system.keyEvent(DIRECTIONS.UP)
        elif key == Qt.Key_Down:
            self.system.keyEvent(DIRECTIONS.DOWN)
    def startGame(self):
        self.startButton.setText('再玩一次')
        self.startButton.setDisabled(True)
        self.gameOver = False
        self.system.start()
        self.timer.start()
