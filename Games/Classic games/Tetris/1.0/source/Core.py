from random import randint, choice
from PyQt5.QtCore import Qt
class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    def __str__(self):
        return "<%s, %s>"%(self.x, self.y)
    def __repr__(self):
        return str(self)
    def __add__(self, vec):
        return Vector(self.x + vec.x, self.y + vec.y)
    def __eq__(self, vec):
        return self.x == vec.x and self.y == vec.y
class Directions:
    Left = Vector(-1, 0)
    Right = Vector(1, 0)
    Down = Vector(0, -1)
    Up = Vector(0, 1)
def enum(*args):
    properties = dict(zip(args, range(len(args))))
    return type("Enum", (), properties)
Blocks = enum("Empty", "Edge", "Z", "S", "I", "L", "J", "O", "T")
class Matrix:
    size = Vector(10, 20)
    deathLine = 16#死亡线y坐标
    def __init__(self):
        self.array = [[Blocks.Empty] * self.size.x for _ in range(self.size.y)]
        self.gameOver = False
        self.cursor = Vector()
        self.tetromino = Tetromino(self)
        self.score = 0
    def __getitem__(self, pos):
        if self.isValid(pos):
            return self.array[pos.y][pos.x]
        return Blocks.Edge
    def __setitem__(self, pos, block):
        if self.isValid(pos):
            self.array[pos.y][pos.x] = block
    def isValid(self, pos):
        return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y
    def isEmpty(self, pos_s):
        for pos in pos_s:
            if self[pos] != Blocks.Empty:
                return False
        return True
    def keyEvent(self, key):
        if not self.gameOver:
            if key == Qt.Key_Left:
                self.tetromino.goL()
            elif key == Qt.Key_Right:
                self.tetromino.goR()
            elif key == Qt.Key_Down:
                self.tetromino.goD()
            elif key == Qt.Key_A:
                self.tetromino.rotateL()
            elif key == Qt.Key_D:
                self.tetromino.rotateR()
    def sweep(self):
        "清除所有满格的行"
        array = [[Blocks.Empty] * self.size.x for _ in range(self.size.y)]
        this = 0
        for self.cursor.y in range(self.deathLine):
            filled = True
            for self.cursor.x in range(self.size.x):
                if self[self.cursor] == Blocks.Empty:
                    filled = False;break
            if not filled:
                array[this] = self.array[self.cursor.y]#未满的行将会存在
                this += 1
            else:
                self.score += 100
        self.array = array
    def update(self):
        if not self.gameOver:
            self.tetromino.update()
        else:
            return 1
    def restart(self):
        self.array = [[Blocks.Empty] * self.size.x for _ in range(self.size.y)]
        self.tetromino.reset()
        self.score = 0
        self.gameOver = False
class Tetromino:
    def __init__(self, matrix):
        self.matrix = matrix
        self.reset()
    def reset(self):
        #重置四格方块
        self.rotate = 0
        self.pos = Vector(randint(1, self.matrix.size.x - 2), self.matrix.size.y - 3)#根据四个block的坐标产生合法的代表坐标
        self.minoType = choice([Blocks.Z, Blocks.S, Blocks.I, Blocks.L, Blocks.J, Blocks.O, Blocks.T])
    def fix(self):
        for pos in self.blockPos():
            self.matrix[pos] = self.minoType
            if pos.y >= self.matrix.deathLine:
                self.matrix.gameOver = True#超过死亡线，GAME OVER
    def rotateR(self):#顺时针
        rotate = (self.rotate + 1) % 4
        if self.matrix.isEmpty(self.blockPos(rotate = rotate)):
            self.rotate = rotate
    def rotateL(self):#逆时针
        rotate = (self.rotate + 3) % 4
        if self.matrix.isEmpty(self.blockPos(rotate = rotate)):
            self.rotate = rotate
    def goL(self):#左移
        pos = self.pos + Directions.Left
        if self.matrix.isEmpty(self.blockPos(pos = pos)):
            self.pos = pos
    def goR(self):#右移
        pos = self.pos + Directions.Right
        if self.matrix.isEmpty(self.blockPos(pos = pos)):
            self.pos = pos
    def goD(self):#下移
        pos = self.pos + Directions.Down
        if self.matrix.isEmpty(self.blockPos(pos = pos)):
            self.pos = pos#下移不会锁定方块，只会在update时判断
    def update(self):
        pos = self.pos + Directions.Down
        if self.matrix.isEmpty(self.blockPos(pos = pos)):
            self.pos = pos
        else:
            self.fix()#锁定方块
            self.matrix.sweep()#清除满格的行
            self.reset()#重置Tetromino
    def blockPos(self, pos = None, rotate = None):
        #获取当前状态下多个block的坐标或给定位置或方向时的坐标
        if pos is None:
            pos = self.pos
        if rotate is None:
            rotate = self.rotate
        if self.minoType == Blocks.Z:
            #0, 2       _ 1, 3
            # _ _     _|_|
            #|_|=|_  |=|_|
            #  |_|_| |_|
            if rotate == 0 or rotate == 2:
                return [pos + Directions.Left, pos, pos + Directions.Down, pos + Vector(1, -1)]
            else:
                return [pos + Directions.Right, pos, pos + Directions.Down, pos + Vector(1, 1)]
        elif self.minoType == Blocks.S:
            #0, 2     _ 1, 3
            #   _ _  |_|_
            # _|=|_| |_|=|
            #|_|_|     |_|
            if rotate == 0 or rotate == 2:
                return [pos + Directions.Right, pos, pos + Directions.Down, pos + Vector(-1, -1)]
            else:
                return [pos + Directions.Left, pos, pos + Directions.Down, pos + Vector(-1, 1)]
        elif self.minoType == Blocks.I:
            # _ 0, 2
            #|_|  _ _ _ _ 1, 3
            #|=| |_|=|_|_|
            #|_|
            #|_|
            if rotate == 0 or rotate == 2:
                return [pos + Directions.Up, pos, pos + Directions.Down, pos + Vector(0, -2)]
            else:
                return [pos + Directions.Left, pos, pos + Directions.Right, pos + Vector(2, 0)]
        
        elif self.minoType == Blocks.L:
            # _ 0     1     _ _ 2     _ 3
            #|_|    _ _ _  |_|_|  _ _|_|
            #|=|_  |_|=|_|   |=| |_|=|_|
            #|_|_| |_|       |_|
            if rotate == 0:
                return [pos + Directions.Up, pos, pos + Directions.Down, pos + Vector(1, -1)]
            elif rotate == 1:
                return [pos + Directions.Left, pos, pos + Directions.Right, pos + Vector(-1, -1)]
            elif rotate == 2:
                return [pos + Directions.Up, pos, pos + Directions.Down, pos + Vector(-1, 1)]
            else:
                return [pos + Directions.Left, pos, pos + Directions.Right, pos + Vector(1, 1)]
        elif self.minoType == Blocks.J:
            #   _0  _1      _ _2     3
            #  |_| |_|_ _  |_|_|  _ _ _
            # _|=| |_|=|_| |=|   |_|=|_|
            #|_|_|         |_|       |_|
            if rotate == 0:
                return [pos + Directions.Up, pos, pos + Directions.Down, pos + Vector(-1, -1)]
            elif rotate == 1:
                return [pos + Directions.Left, self.pos, pos + Directions.Right, pos + Vector(-1, 1)]
            elif rotate == 2:
                return [pos + Directions.Up, pos, pos + Directions.Down, pos + Vector(1, 1)]
            else:
                return [pos + Directions.Left, pos, pos + Directions.Right, pos + Vector(1, -1)]
        elif self.minoType == Blocks.O:
            # _ _
            #|=|_|
            #|_|_|
            return [pos + Directions.Down, pos, pos + Directions.Right, pos + Vector(1, -1)]
        elif self.minoType == Blocks.T:
            # _ _ _ 0   _ 1   _ 2   _ 3
            #|_|=|_|  _|_|  _|_|_  |_|
            #  |_|   |_|=| |_|=|_| |=|_|
            #          |_|         |_|
            if rotate == 0:
                return [pos + Directions.Left, pos, pos + Directions.Right, pos + Directions.Down]
            elif rotate == 1:
                return [pos + Directions.Left, pos, pos + Directions.Up, pos + Directions.Down]
            elif rotate == 2:
                return [pos + Directions.Up, pos, pos + Directions.Left, pos + Directions.Right]
            else:
                return [pos + Directions.Up, pos, pos + Directions.Right, pos + Directions.Down]
##from pprint import pprint
##m = Matrix()
##m.restart()
##print(m[Vector(0, 0)])
##for i in range(40):
##    print(m.update())
##    pos_s = m.tetromino.blockPos()
##    for y in range(m.size.y):
##        for x in range(m.size.x):
##            if Vector(x, y) in pos_s:
##                print(m.tetromino.minoType, end = ' ')
##            else:
##                print(m[Vector(x, y)], end = ' ')
##        print()
