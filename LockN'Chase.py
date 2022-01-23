import pygame
import math
import random
import copy
import json
from os.path import isfile

pygame_icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(pygame_icon)
pygame. display. set_caption("Lock n' Chase")

THIEF_SIZE = 32
BLOCK_SIZE = 32

pygame.init()
pygame.font.init()


sprites_png = pygame.image.load('images/sprites.png')
sprites_png.set_colorkey((0, 0, 0))
launchScreen_png = pygame.image.load('images/launchScreen.png')
endScreen_png = pygame.image.load('images/endScreen.png')
coin_png = pygame.image.load('images/coin.png')

Font = Font=pygame.font.SysFont('chiller',  70, True)
FontColor = (255, 242, 0)


# 23 comprimento /  14 altura /  0: espaço vazio ; 1: parede ;  2: moeda
originLevel = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # topo
    [0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0],  # 2 --- moeda
    [0, 0, 0, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 0, 0],  # 3 --- porta horizontal
    [0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0],  # 4 --- porta vertical
    [1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 2, 2, 1, 2, 1, 2, 0, 2, 1, 2, 1, 2, 2, 2, 0, 0, 0, 1],  # entrada 2
    [1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],  # entrada 1
    [1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],  # base
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                ]

level = copy.deepcopy(originLevel)

SCREEN_SIZE = (len(level[0]) * BLOCK_SIZE, len(level) * BLOCK_SIZE)
screen = pygame.display.set_mode(SCREEN_SIZE)


class Game:
    def __init__(self, score):
        self.collected = 0
        self.lives = 2
        self.score = score
        self.scoreCol = 15
        self.scoreRow = 1
        self.thiefStart = (13, 16)
        self.thief = Thief(self.thiefStart[0], self.thiefStart[1])
        self.total = 97
        self.goldScore = 10
        self.gameOver = False
        self.detective = [Detective(3, 8, 'red'), Detective(3, 10, 'blue'), Detective(19, 8, 'yellow'), Detective(19, 10, 'green')]
        self.door = False
        self.doorTimer = 0
        self.doorCount = 0
        self.doorCol = 0
        self.doorRow = 0
        self.bagTimer = 0
        self.bagCol = 11
        self.bagRow = 8
        self.bagScore = 100
        self.spriteTimer = 0
        self.spriteCount = 0
        self.pause = True
        self.launchScreen = True
        self.start = False
        self.endScreen = False
        self.gotbag = False
        self.highscore = 0
        self.win = False
        self.lost = False

    def update(self):
        self.draw()
        if not self.pause:
            if not self.launchScreen:
                self.thief.update()
                for det in self.detective:
                    det.update()

        self.getHighscore()
        self.changeSprite()
        self.touch()
        self.getScore()
        self.displayLives()
        self.displayScore()
        self.outBase()
        self.spawnBag()
        if self.door or self.doorCount == 1:
            self.placeDoor()
        if self.collected == self.total:
            self.collectedAll()
        if self.gameOver:
            self.ended()
        self.started()


    def draw(self):
        screen.fill(pygame.Color("black"))
        if self.launchScreen:
            strHighscore = Font.render(str(self.highscore), True, FontColor)
            screen.blit(launchScreen_png, (0, 0))
            screen.blit(strHighscore, (11.4 * BLOCK_SIZE, 6 * BLOCK_SIZE))
        elif self.gameOver:
            screen.blit(endScreen_png, (0, 0))
            strHighscore = Font.render(str(self.highscore), True, FontColor)
            strScore = Font.render(str(self.score), True, FontColor)
            screen.blit(strScore, (self.scoreCol * BLOCK_SIZE, self.scoreRow * BLOCK_SIZE))
            screen.blit(strHighscore, (11 * BLOCK_SIZE, 8 * BLOCK_SIZE))

        else:
            for row in range(len(level)):
                for col in range(len(level[row])):
                    if level[row][col] == 1:          # parede
                        pygame.draw.rect(screen, pygame.Color('darkblue'),
                                         (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(screen, pygame.Color('darkgray'),
                                         (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
                    if level[row][col] == 2:          # moeda
                        screen.blit(coin_png, (col * BLOCK_SIZE + BLOCK_SIZE // 4, row * BLOCK_SIZE + BLOCK_SIZE // 4))
                    if level[row][col] == 3:          # porta
                        pygame.draw.rect(screen, pygame.Color('darkgreen'), (col * BLOCK_SIZE, row * BLOCK_SIZE + BLOCK_SIZE // 2, BLOCK_SIZE, BLOCK_SIZE // 8))
                    if level[row][col] == 4:          # porta
                        pygame.draw.rect(screen, pygame.Color('darkgreen'), (col * BLOCK_SIZE + BLOCK_SIZE // 2 - 1, row * BLOCK_SIZE, BLOCK_SIZE // 8, BLOCK_SIZE))
                    if level[row][col] == 5:          # porta
                        pygame.draw.rect(screen, pygame.Color('darkgreen'), (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE // 8))
                    if level[row][col] == 6:          # saco
                        screen.blit(sprites_png, (col * BLOCK_SIZE, row * BLOCK_SIZE), (342, 98, 30, 30))

            if not self.pause or (self.pause and not self.lost and not self.win):
                if self.thief.dir == 0:
                    screen.blit(sprites_png, (self.thief.col * BLOCK_SIZE, self.thief.row * BLOCK_SIZE), (1 + 29 * (self.spriteCount % 2), 3, 30, 30))
                if self.thief.dir == 2:
                    screen.blit(sprites_png, (self.thief.col * BLOCK_SIZE, self.thief.row * BLOCK_SIZE), (62 + 29 * (self.spriteCount % 2), 3, 30, 30))
                if self.thief.dir == 1:
                    screen.blit(sprites_png, (self.thief.col * BLOCK_SIZE, self.thief.row * BLOCK_SIZE), (125 + 29 * (self.spriteCount % 2), 3, 30, 30))
                if self.thief.dir == 3:
                    screen.blit(sprites_png, (self.thief.col * BLOCK_SIZE, self.thief.row * BLOCK_SIZE), (187 + 29 * (self.spriteCount % 2), 3, 30, 30))
            elif self.win:
                screen.blit(sprites_png, (self.thief.col * BLOCK_SIZE, self.thief.row * BLOCK_SIZE), (249 + 29 * (self.spriteCount % 2), 3, 30, 30))
            elif self.lost:
                screen.blit(sprites_png, (self.thief.col * BLOCK_SIZE, self.thief.row * BLOCK_SIZE), (310 + 31 * (self.spriteCount % 4), 3, 30, 30))
            for det in self.detective:
                if det.color == 'red':
                    height = 34
                elif det.color == 'yellow':
                    height = 67
                elif det.color == 'blue':
                    height = 98
                elif det.color == 'green':
                    height = 128

                if self.win:
                    if self.spriteCount % 3 != 0:
                        area = (0 + 31 * (self.spriteCount % 3), 158, 31, 30)
                    else: area = (0 + 31 * (self.spriteCount % 3), 158, 30, 30)

                else:
                    if det.dir == 0:
                        area = (2 + 29 * (self.spriteCount % 2), height, 30, 30)
                    elif det.dir == 2:
                        area = (64 + 29 * (self.spriteCount % 2), height, 30, 30)
                    elif det.dir == 1:
                        area = (125 + 29 * (self.spriteCount % 2), height, 30, 30)
                    elif det.dir == 3:
                        area = (187 + 29 * (self.spriteCount % 2), height, 30, 30)

                screen.blit(sprites_png, (det.col * BLOCK_SIZE, det.row * BLOCK_SIZE), area)

                if self.gotbag and self.bagTimer < 60:
                    screen.blit(sprites_png, ((self.bagCol + 0.5) * BLOCK_SIZE, (self.bagRow - 0.2) * BLOCK_SIZE),
                                (470, 52, 40, 10))

            strScore = Font.render(str(self.score), True, FontColor)
            screen.blit(strScore, (self.scoreCol * BLOCK_SIZE, self.scoreRow * BLOCK_SIZE))


    def changeSprite(self):
        self.spriteTimer += 1
        if self.spriteTimer == 30:
            self.spriteCount += 1
            self.spriteTimer = 0


    def started(self):
        if self.start and self.launchScreen:
            self.launchScreen = False
            self.pause = False
        self.start = False

    def ended(self):
        global game
        if self.score > self.highscore:
            high = {"highscore": self.score}
            json.dump(high, open("highscore.txt", "w"))
        if self.start:
            global level
            game = Game(0)
            level = copy.deepcopy(originLevel)

    def getScore(self):
            if self.thief.row % 1.0 == 0 and self.thief.col % 1.0 == 0:
                if level[int(self.thief.row)][int(self.thief.col)] == 2:
                    level[int(self.thief.row)][int(self.thief.col)] = 0
                    self.score += self.goldScore
                    self.collected += 1
                if level[int(self.thief.row)][int(self.thief.col)] == 6:
                    level[int(self.thief.row)][int(self.thief.col)] = 0
                    self.score += self.bagScore
                    self.bagTimer = 0
                    self.gotbag = True
            if self.bagTimer  == 60:
                self.gotbag = False

    def getHighscore(self):
        if isfile("highscore.txt"):
            a = json.load(open("highscore.txt"))
            self.highscore = a['highscore']
        else:
            high = {"highscore":0}
            json.dump(high, open("highscore.txt","w"))
            self.highscore = 0


    def displayScore(self):
        global Font, FontColor

        if self.gameOver or self.launchScreen:
            self.scoreCol = 10
            self.scoreRow = 6
            Font = pygame.font.SysFont('chiller',  55, False)
            FontColor = (140, 45, 25)
        else:
            self.scoreCol = 15
            self.scoreRow = 1
            Font = pygame.font.SysFont('chiller',  70, True)
            FontColor = (255, 242, 0)

    def touch(self):
        for det in self.detective:
            if math.fabs(det.col - self.thief.col) < 0.75 and math.fabs(det.row - self.thief.row) < 0.75:
                if not self.lost:
                    self.lost = True
                    self.pause = True
                    self.bagTimer = 0
                    self.spriteCount = 0
                if self.bagTimer == 300:
                    self.lost = False

                    if self.lives == 0:
                        self.pause = True
                        self.gameOver = True

                    else:
                        self.lives -= 1
                        self.reset()

    def collectedAll(self):
        if self.pause == False:
            self.pause = True
            self.win = True
            self.bagTimer = 0

        if self.bagTimer == 300:
            self.reset()
        if self.bagTimer == 420:
            self.pause = False



    def outBase(self):
        if self.thief.row == self.thiefStart[0] - 1:
            level[self.thiefStart[0]][self.thiefStart[1]] = 5

    def placeDoor(self):
        self.doorTimer += 1
        if self.thief.row % 1 == 0 and self.thief.col % 1 == 0:
            self.door = False
        if self.doorCount == 0:
            if self.thief.row % 1 == 0 and self.thief.col % 1 == 0:
                self.doorRow = int(self.thief.row)
                self.doorCol = int(self.thief.col)
                if not canMove(self.doorRow + 1, self.doorCol) and not canMove(self.doorRow - 1, self.doorCol):
                    level[self.doorRow][self.doorCol] = 4
                    self.doorCount = 1
                    self.doorTimer = 0
                    self.draw()
                elif not canMove(self.doorRow, self.doorCol + 1) and not canMove(self.doorRow, self.doorCol - 1):
                    level[self.doorRow][self.doorCol] = 3
                    self.doorCount = 1
                    self.doorTimer = 0
                    self.draw()
        if self.doorCount == 1 and self.doorTimer == 300:
            self.doorCount = 0
            self.doorTimer = 0
            level[self.doorRow][self.doorCol] = 0
        return

    def displayLives(self):
        index = 3
        if not self.gameOver and not self.launchScreen:
            if not self.lost and not self.win:
                for number in range(0, self.lives):
                    screen.blit(sprites_png, ((2 + 2 * index) * BLOCK_SIZE, 14 * BLOCK_SIZE), (248, 35, 62, 30))
                    index -= 1
            elif self.lost:
                if self.lives == 1:
                    screen.blit(sprites_png,(8 * BLOCK_SIZE + self.bagTimer // 1.6, 14 * BLOCK_SIZE), (248 + self.spriteCount % 2 + 61 * (self.spriteCount % 2), 35, 62, 29))
                elif self.lives == 2:
                    screen.blit(sprites_png, (8 * BLOCK_SIZE + self.bagTimer / 1.6, 14 * BLOCK_SIZE), (248 + self.spriteCount % 2 + 61 * (self.spriteCount % 2), 35, 62, 29))
                    screen.blit((sprites_png), (6 * BLOCK_SIZE + self.bagTimer // 4, 14 * BLOCK_SIZE), (248 + self.spriteCount % 2 + 61 * (self.spriteCount % 2), 35, 62, 29))
            elif self.win:
                if self.lives == 0:
                    screen.blit(sprites_png,(1 * BLOCK_SIZE + self.bagTimer // 1.4, 14 * BLOCK_SIZE), (248 + self.spriteCount % 2 + 61 * (self.spriteCount % 2), 35, 62, 29))
                elif self.lives == 1:
                    screen.blit(sprites_png, (8 * BLOCK_SIZE, 14 * BLOCK_SIZE), (248, 35, 62, 30))
                    screen.blit(sprites_png,(1 * BLOCK_SIZE + self.bagTimer // 1.9, 14 * BLOCK_SIZE), (248 + self.spriteCount % 2 + 61 * (self.spriteCount % 2), 35, 62, 29))
                else:
                    for number in range(0, self.lives):
                        screen.blit(sprites_png, ((2 + 2 * index) * BLOCK_SIZE, 14 * BLOCK_SIZE), (248, 35, 62, 30))
                        index -= 1

    def spawnBag(self):
        self.bagTimer += 1
        if self.bagTimer == 300:
            level[self.bagRow][self.bagCol] = 6
        if self.bagTimer == 600:
            level[self.bagRow][self.bagCol] = 0
            self.bagTimer = 0
        return

    def reset(self):
        global level

        self.pause = False
        level[self.thiefStart[0]][self.thiefStart[1]] = 0
        level[self.bagRow][self.bagCol] = 0
        self.thief.row = self.thiefStart[0]
        self.thief.col = self.thiefStart[1]
        self.thief.dir = self.thief.newDir = 2
        self.detective = [Detective(3, 8, 'red'), Detective(3, 10, 'blue'), Detective(19, 8, 'yellow'), Detective(19, 10, 'green')]
        self.bagTimer = 0
        if self.doorCount == 1:
            level[self.doorRow][self.doorCol] = 0
            self.doorCount = 0
            self.doorTimer = 0

        if self.win:
            self.win = False
            level = copy.deepcopy(originLevel)
            self.collected = 0
            if self.lives < 2:
                self.lives += 1
        return


class Thief:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.thiefSpeed = 1 / BLOCK_SIZE * 2
        self.dir = 2  # 0: cima, 1: direita , 2: baixo, 3: esquerda
        self.newDir = 2

    def update(self):
        if self.newDir == 0:
            if canMove(math.floor(self.row - self.thiefSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.thiefSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 1:
            if canMove(self.row, math.ceil(self.col + self.thiefSpeed)) and self.row % 1.0 == 0:
                self.col += self.thiefSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 2:
            if canMove(math.ceil(self.row + self.thiefSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.thiefSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 3:
            if canMove(self.row, math.floor(self.col - self.thiefSpeed)) and self.row % 1.0 == 0:
                self.col -= self.thiefSpeed
                self.dir = self.newDir
                return

        if self.dir == 0:
            if canMove(math.floor(self.row - self.thiefSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.thiefSpeed
        elif self.dir == 1:
            if int(self.col) == len(level[0]) - 2:
                self.col = 1
            if canMove(self.row, math.ceil(self.col + self.thiefSpeed)) and self.row % 1.0 == 0:
                self.col += self.thiefSpeed
        elif self.dir == 2:
            if canMove(math.ceil(self.row + self.thiefSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.thiefSpeed
        elif self.dir == 3:
            if self.col <= 2:
                self.col = len(level[0]) - 2
            if canMove(self.row, math.floor(self.col - self.thiefSpeed)) and self.row % 1.0 == 0:
                self.col -= self.thiefSpeed


class Detective:
    def __init__(self, col, row, color):
        self.row = row
        self.color = color
        self.col = col
        self.newDir = 0
        self.detSpeed = 1.5 / BLOCK_SIZE
        self.chaseCounter = 300
        self.chaseTimer = 0
        if self.col == 3:
            self.dir = 1
        else:
            self.dir = 3


    def checkSide(self, row, col):
        totaldirections = []
        if canMove(col, row + 1):
            totaldirections.append(2)
        if canMove(col, row - 1):
            totaldirections.append(0)
        if canMove(col + 1, row):
            totaldirections.append(1)
        if canMove(col - 1, row):
            totaldirections.append(3)

        return totaldirections


    def chase(self):
        if math.fabs(self.row - game.thief.row) <= math.fabs(
                self.col - game.thief.col):  # se estiver mais afastado horizontalmente do que verticalmente
            if self.col < game.thief.col:  # se estiver à esquerda do ladrão
                if canMove(self.row, self.col + 1):  # se conseguir andar para a direita
                    self.newDir = 1
                else:  # se não conseguir andar para a direita
                    if canMove(self.row - 1, self.col) and canMove(self.row + 1,
                                                                   self.col):  # se conseguir andar para cima e baixo
                        if self.row < game.thief.row:  # se estiver a cima do ladrão
                            self.newDir = 2
                        elif self.row >= game.thief.row:  # se estiver em baixo do ladrão
                            self.newDir = 0
                    elif canMove(self.row - 1, self.col) and not canMove(self.row + 1,
                                                                         self.col):  # se só conseguir andar para cima
                        self.newDir = 0
                    elif not canMove(self.row - 1, self.col) and canMove(self.row + 1,
                                                                         self.col):  # se só conseguir andar para baixo
                        self.newDir = 2
                    else:
                        self.newDir = 3
            elif self.col >= game.thief.col:  # se estiver à direita do ladrão
                if canMove(self.row, self.col - 1):  # se conseguir andar para a esquerda
                    self.newDir = 3
                else:  # se não conseguir andar para a esquerda
                    if canMove(self.row - 1, self.col) and canMove(self.row + 1,
                                                                   self.col):  # se conseguir andar para cima e baixo
                        if self.row < game.thief.row:  # se estiver a cima do ladrão
                            self.newDir = 2
                        elif self.row >= game.thief.row:  # se estiver em baixo do ladrão
                            self.newDir = 0
                    elif canMove(self.row - 1, self.col) and not canMove(self.row + 1,
                                                                         self.col):  # se só conseguir andar para cima
                        self.newDir = 0
                    elif not canMove(self.row - 1, self.col) and canMove(self.row + 1,
                                                                         self.col):  # se só conseguir andar para baixo
                        self.newDir = 2
                    else:
                        self.newDir = 1


        elif math.fabs(self.row - game.thief.row) > math.fabs(
                self.col - game.thief.col):  # se estiver mais afastado verticalmente do que horizontalmente
            if self.row <= game.thief.row:  # se estiver acima do ladrão
                if canMove(self.row + 1, self.col):
                    self.newDir = 2
                else:  # se não conseguir andar para baixo
                    if canMove(self.row, self.col - 1) and canMove(self.row,
                                                                   self.col + 1):  # se conseguir andar para a direita e para a esquerda
                        if self.col <= game.thief.col:  # se estiver à esquerda do ladrão
                            self.newDir = 1
                        else:  # se estiver à direita do ladrão
                            self.newDir = 3
                    elif canMove(self.row, self.col - 1) and not canMove(self.row,
                                                                         self.col + 1):  # se só conseguir andar para a esquerda
                        self.newDir = 3
                    elif not canMove(self.row, self.col - 1) and canMove(self.row,
                                                                         self.col + 1):  # se só conseguir andar para a direita
                        self.newDir = 1
                    else:
                        self.newDir = 0

            elif self.row > game.thief.row:  # se estiver abaixo do ladrão
                if canMove(self.row - 1, self.col):  # se conseguir andar para cima
                    self.newDir = 0
                else:  # se não conseguir andar para cima
                    if canMove(self.row, self.col - 1) and canMove(self.row,
                                                                   self.col + 1):  # se conseguir andar para a direita e para a esquerda
                        if self.col <= game.thief.col:  # se estiver à esquerda do ladrão
                            self.newDir = 1
                        else:  # se estiver à direita do ladrão
                            self.newDir = 3
                    elif canMove(self.row, self.col - 1) and not canMove(self.row,
                                                                         self.col + 1):  # se só conseguir andar para a esquerda
                        self.newDir = 3
                    elif not canMove(self.row, self.col - 1) and canMove(self.row,
                                                                         self.col + 1):  # se só conseguir andar para a direita
                        self.newDir = 1
                    else:
                        self.newDir = 2
        return

    def update(self):
        a = [1]

        if self.chaseTimer > self.chaseCounter * 2:
            self.chaseTimer = 0
        if self.col % 1 == 0 and self.row % 1 == 0:
            a = self.checkSide(round(self.col), round(self.row))

            if len(a) == 3 or len(a) == 4 and self.chaseTimer <= self.chaseCounter:
                self.newDir = random.choice(a)
            if (len(a) == 3 or len(a) == 4) and self.chaseCounter < self.chaseTimer <= self.chaseCounter * 2:
                self.chase()
        self.chaseTimer += 1

        if self.newDir == 0:
            if canMove(math.floor(self.row - self.detSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.detSpeed
                self.dir = self.newDir
                self.newDir = None

        elif self.newDir == 1:
            if canMove(self.row, math.ceil(self.col + self.detSpeed)) and self.row % 1.0 == 0:
                self.col += self.detSpeed
                self.dir = self.newDir
                self.newDir = None

        elif self.newDir == 2:
            if canMove(math.ceil(self.row + self.detSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.detSpeed
                self.dir = self.newDir
                self.newDir = None

        elif self.newDir == 3:
            if canMove(self.row, math.floor(self.col - self.detSpeed)) and self.row % 1.0 == 0:
                self.col -= self.detSpeed
                self.dir = self.newDir
                self.newDir = None

        if self.dir == 0:
            if canMove(math.floor(self.row - self.detSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.detSpeed
            else:
                self.row = int(self.row)
                self.newDir = random.randint(0,4)

        elif self.dir == 1:
            if self.col >= len(level[0]) - 3:
                self.col = 2
            if canMove(self.row, math.ceil(self.col + self.detSpeed)) and self.row % 1.0 == 0:
                self.col += self.detSpeed
            else:
                self.col = round(self.col)
                self.newDir = random.randint(0,4)

        elif self.dir == 2:
            if canMove(math.ceil(self.row + self.detSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.detSpeed
            else:
                self.row = round(self.row)
                self.newDir = random.randint(0,4)

        elif self.dir == 3:
            if self.col <= 2:
                self.col = len(level[0]) - 3
            if canMove(self.row, math.floor(self.col - self.detSpeed)) and self.row % 1.0 == 0:
                self.col -= self.detSpeed
            else:
                self.col = round(self.col)
                self.newDir = random.randint(0,4)





def canMove(row, col):
    if col == -1 or col == len(level[0]):
        return True
    elif level[int(row)][int(col)] != 1 and level[int(row)][int(col)] != 3 and level[int(row)][int(col)] != 4 and level[int(row)][int(col)] != 5:
        return True
    return False


running = True
game = Game(0)
clock = pygame.time.Clock()
while running:
    game.update()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key == pygame.K_RETURN:
                game.start = True
            if not game.pause:
                if ev.key == pygame.K_UP:
                    game.thief.newDir = 0
                elif ev.key == pygame.K_RIGHT:
                    game.thief.newDir = 1
                elif ev.key == pygame.K_DOWN:
                    game.thief.newDir = 2
                elif ev.key == pygame.K_LEFT:
                    game.thief.newDir = 3
                elif ev.key == pygame.K_SPACE:
                    game.door = True
    pygame.display.flip()
    clock.tick(60)
