#Core definitions
from random import choice
##### Vector #####
class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    def __add__(self, vec):
        return Vector(self.x + vec.x, self.y + vec.y)
    def __floordiv__(self, integer):
        return Vector(self.x // integer, self.y // integer)
    def __mul__(self, integer):
        return Vector(self.x * integer, self.y * integer)
    def __hash__(self):
        return hash((self.x, self.y))
    def __eq__(self, vec):
        return self.x == vec.x and self.y == vec.y
    def __str__(self):
        return "<%s, %s>"%(self.x, self.y)
    def __repr__(self):
        return self.__str__()
zeroVector = Vector(0, 0)
##### Constant Data #####
def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('enum', (), enums)
PIXEL_TYPES = enum('EMPTY', 'BARRIER', 'SNAKE_BODY', 'FOOD', 'SNAKE_HEAD')
SNAKE_STATES = enum('NOTHING', 'GOT_FOOD', 'CRASHED', 'BITED_SELF')
class DIRECTIONS:
    UP = Vector(0, -1)
    DOWN = Vector(0, 1)
    RIGHT = Vector(1, 0)
    LEFT = Vector(-1, 0)
##### Matrix #####
class Matrix:
    def __init__(self, size):
        self.size = size
        self.initData()
        self.barrierPos = Vector(-1, -1)
    def __getitem__(self, pos):
        if self.isValid(pos):
            return self.array[pos.y][pos.x]#注意顺序
        else:
            return PIXEL_TYPES.BARRIER
    def __setitem__(self, pos, pixelType):
        if self.isValid(pos):
            if pixelType == PIXEL_TYPES.EMPTY:
                self.emptyPos.add(pos)
            else:
                self.emptyPos.discard(pos)
            self.array[pos.y][pos.x] = pixelType
    def resetFood(self):
        pos = choice(list(self.emptyPos))
        self[pos] = PIXEL_TYPES.FOOD
    def resetBarrier(self):
        self[self.barrierPos] = PIXEL_TYPES.EMPTY
        self.barrierPos = choice(list(self.emptyPos))
        self[self.barrierPos] = PIXEL_TYPES.BARRIER
    def initData(self):
        self.array = [[PIXEL_TYPES.EMPTY] * self.size.x for _ in range(self.size.y)]#注意列表生成式是必须的，防止浅复制
        self.emptyPos = {Vector(x, y) for x in range(self.size.x) for y in range(self.size.y)}#空位坐标集合
    def isValid(self, pos):
        return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y
##### Snake #####
class Node:
    def __init__(self, pos, matrix):
        self.matrix = matrix
        self.pos = pos#需要先声明
        self.move(pos)
        self.prev = self.next = None#支持双向链表
    def setPrev(self, node):
        self.prev = node
    def setNext(self, node):
        self.next = node
    def setPos(self, pos):
        self.pos = pos
    def move(self, pos):#改变坐标并更新数据
        self.matrix[self.pos] = PIXEL_TYPES.EMPTY#腾空原先的位置
        self.setPos(pos)
        self.matrix[self.pos] = PIXEL_TYPES.SNAKE_HEAD#根据设计，移动的节点总是head
    def turnToBody(self):
        self.matrix[self.pos] = PIXEL_TYPES.SNAKE_BODY
#operations
def connect(a, b):
    a.setNext(b)
    b.setPrev(a)
def disconnect(a, b):
    a.setNext(None)
    b.setPrev(None)
class Snake:
    def __init__(self, node, matrix):
        self.matrix = matrix
        self.matrix.resetFood()
        self.matrix.resetBarrier()
        self.head = self.tail = node
        self.direction = DIRECTIONS.LEFT
        self.length = 1
    def setDirection(self, direction):
        if direction + self.direction == zeroVector:#方向完全相反
            return
        self.direction = direction
    def newHeadPos(self):
        return self.head.pos + self.direction
    def update(self):
        pos = self.newHeadPos()
        pixelType = self.matrix[pos]
        if pixelType == PIXEL_TYPES.EMPTY:
            self._goDirectly(pos, pixelType)
            return SNAKE_STATES.NOTHING
        elif pixelType == PIXEL_TYPES.FOOD:
            new = Node(pos, self.matrix)#生成新的节点并覆盖掉食物像素
            connect(new, self.head)
            self.head.turnToBody()#原先的head的像素变为body
            self.head = new
            self.length += 1
            return SNAKE_STATES.GOT_FOOD
        elif pixelType == PIXEL_TYPES.BARRIER:
            return SNAKE_STATES.CRASHED
        elif pixelType == PIXEL_TYPES.SNAKE_BODY:
            if pos == self.tail.pos:
                self._goDirectly(pos, pixelType)
                return SNAKE_STATES.NOTHING
            else:
                return SNAKE_STATES.BITED_SELF
    def _goDirectly(self, pos, pixelType):
        if self.length == 1:
            self.head.move(pos)
        else:
            connect(self.tail, self.head)
            self.head = self.tail
            self.tail = self.tail.prev
            disconnect(self.tail, self.head)
            self.head.move(pos)
            self.head.next.turnToBody()
class System:
    #OS
    MATRIX_SIZE = Vector(30, 20)
    SNAKE_INITIAL_POS = MATRIX_SIZE // 2
    def __init__(self):
        self.matrix = Matrix(self.MATRIX_SIZE)
        self.start()
    def update(self):
        state = self.snake.update()
        if state == SNAKE_STATES.GOT_FOOD:
            self.foodScore += 1
            self.matrix.resetFood()#重置食物像素
            self.matrix.resetBarrier()
        elif state == SNAKE_STATES.CRASHED:
            return 1
        elif state == SNAKE_STATES.BITED_SELF:
            return 1
    def keyEvent(self, direction):
        self.snake.setDirection(direction)
    def start(self):
        self.matrix.initData()
        self.snake = Snake(Node(self.SNAKE_INITIAL_POS, self.matrix), self.matrix)
        self.foodScore = 0#食物分
##from pprint import pprint
##s = System()
##s.matrix[Vector(12, 10)] = PIXEL_TYPES.FOOD
##s.matrix[Vector(13, 10)] = PIXEL_TYPES.FOOD
##for _ in range(10):
##    print(s.update())
##    pprint(s.matrix.array)
