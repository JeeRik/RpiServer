import math

import numpy as np

import Const
from Defs import Colors, MODULES
from Firepworks import Fireworks
from Modular import Modular, Graphic
from Modules import RainbowModule
from Swarovski import Clock


class Segment:
    """Segment of cannonballs flying in opposite directions. Upon contact, a flash is created"""

    def __init__(self, cannon, start, end, speed=1):
        self.cannon = cannon
        self.start = start
        self.end = end if start < end else end + Const.LED_COUNT

        # cannonballs: [pos, color]
        self.clockwise = []
        self.countercw = []

        # flashes: [position, color, current dim ratio, dim ratio increment, current width, width increment]
        #   see Fireworks.addFlash(...)
        self.flashes = []

        self.ballSpeed = speed
        self.headLen = speed * 2
        self.tailLen = speed * 5

    def fire(self, color, direction):
        if direction > 0:
            self.countercw.append([self.start, color])
        else:
            self.clockwise.append([self.end, color])

    def addFlash(self, pos, color=Colors.WHITE):
        self.flashes = Fireworks.filterFlashes(self.flashes)
        self.flashes.append([pos, color, 0, self.ballSpeed * 6, self.tailLen, self.ballSpeed])

    def paint(self, block):

        for c in self.clockwise:
            Colors.addGradient(block, c[0], c[0] + self.tailLen, c[1], Colors.BLACK)
            Colors.addGradient(block, c[0] - self.headLen, c[0], Colors.BLACK, c[1])
            c[0] -= self.ballSpeed

        for c in self.countercw:
            Colors.addGradient(block, c[0], c[0] + self.tailLen, c[1], Colors.BLACK)
            Colors.addGradient(block, c[0] - self.headLen, c[0], Colors.BLACK, c[1])
            c[0] += self.ballSpeed

        if len(self.clockwise) > 0:
            if len(self.countercw) == 0:
                if self.clockwise[0][0] <= self.start:
                    # self.addFlash(self.clockwise[0][0], self.clockwise[0][1])
                    self.addFlash(self.clockwise[0][0], self.cannon.collisionColor)
                    self.clockwise = self.clockwise[1:]
            else:
                if self.clockwise[0][0] <= self.countercw[0][0]:
                    c1 = self.clockwise[0][1]
                    c2 = self.countercw[0][1]

                    self.addFlash(self.clockwise[0][0], self.cannon.explosionColor)
                    # self.addFlash(self.clockwise[0][0], [max(c1[0], c2[0]), max(c1[1], c2[1]), max(c1[2], c2[2])])

                    self.clockwise = self.clockwise[1:]
                    self.countercw = self.countercw[1:]
        else:
            if len(self.countercw) > 0:
                if self.countercw[0][0] >= self.end:
                    # self.addFlash(self.countercw[0][0], self.countercw[0][1])
                    self.addFlash(self.countercw[0][0], self.cannon.collisionColor)
                    self.countercw = self.countercw[1:]

        for flash in self.flashes:
            Fireworks.addFlash(block, flash)


class Tower:
    @staticmethod
    def getTimeToNextShot():
        return (np.random.poisson(500) % 200)

    def __init__(self, cannon, pos, clockwiseSegment, countercwSegment, color=Colors.WHITE):
        self.cannon = cannon
        self.pos = pos
        self.clockwiseSegment = clockwiseSegment
        self.countercwSegment = countercwSegment
        self.color = color

        self.nextClockwiseShot = self.getTimeToNextShot()
        self.nextCountercwShot = self.getTimeToNextShot()
        self.counter = 0

    def paint(self, block):
        # Paint tower
        Colors.addGradient(block, self.pos - self.cannon.towerWidth, self.pos, Colors.BLACK, self.color)
        Colors.addGradient(block, self.pos, self.pos + self.cannon.towerWidth, self.color, Colors.BLACK)

        # Fire clockwise
        if self.nextClockwiseShot <= self.counter:
            self.nextClockwiseShot += self.getTimeToNextShot()
            self.clockwiseSegment.fire(self.color, -1)

        # Fire counterclockwise
        if self.nextCountercwShot <= self.counter:
            self.nextCountercwShot += self.getTimeToNextShot()
            self.countercwSegment.fire(self.color, 1)

        self.counter += 1


class RainbowTower(Tower):
    def __init__(self, cannon, pos, clockwiseSegment, countercwSegment, colorAngle):
        color = RainbowModule.wheel(colorAngle)
        self.initColorAngle = colorAngle
        self.initPos = pos
        Tower.__init__(self, cannon, pos + Clock.getMinuteNeedlePos(), clockwiseSegment, countercwSegment, color)

    def paint(self, block):
        self.color = RainbowModule.wheel(int(math.floor(self.initColorAngle + self.counter*0.2)))
        self.pos = self.initPos + Clock.getMinuteNeedlePos()
        self.countercwSegment.start = self.pos
        if self.countercwSegment.start > self.countercwSegment.end:
            self.countercwSegment.end += Const.LED_COUNT
        self.clockwiseSegment.end = self.pos
        if self.clockwiseSegment.end < self.clockwiseSegment.start:
            self.clockwiseSegment.end += Const.LED_COUNT
        Tower.paint(self, block)

class Cannon(Modular):

    name = "Cannon shootout"
    key = "cannon"
    help = "Usage >> m cannon [mode]<<. Modes are \"duel\", \"ambient\", \"rainbow\"."

    mode = "rainbow"

    @staticmethod
    def configure(args):
        if len(args) > 0:
            Cannon.mode = args[0]

    @staticmethod
    def getinstance():
        return Cannon(Cannon.mode)


    def __init__(self, mode = "rainbow"):
        Modular.__init__(self)

        self.counter = 0

        if mode == "ambient":
            themeColor = [0x60, 0x4a, 0x28]
            # themeColor = [0xc0, 0x98, 0x48]
            self.segments = [
                Segment(self, Const.LED_CORNERS[0], Const.LED_CORNERS[1], 1),
                Segment(self, Const.LED_CORNERS[1], Const.LED_CORNERS[2], 1),
                Segment(self, Const.LED_CORNERS[2], Const.LED_CORNERS[3], 1),
                Segment(self, Const.LED_CORNERS[3], Const.LED_CORNERS[0] + Const.LED_COUNT, 1),
            ]
            self.towers = [
                Tower(self, Const.LED_CORNERS[0], self.segments[3], self.segments[0], themeColor),
                Tower(self, Const.LED_CORNERS[1], self.segments[0], self.segments[1], themeColor),
                Tower(self, Const.LED_CORNERS[2], self.segments[1], self.segments[2], themeColor),
                Tower(self, Const.LED_CORNERS[3], self.segments[2], self.segments[3], themeColor),
            ]
            self.explosionColor = themeColor
            self.collisionColor = map(lambda x: min(x*2, 0xff), themeColor)
            self.towerWidth = 20

        elif mode == "rainbow":
            print("Initializing Cannon.rainbow")
            now = Clock.getMinuteNeedlePos()
            arcLen = Const.LED_COUNT / 3

            self.segments = [
                Segment(self, now, now + arcLen, 1),
                Segment(self, now + arcLen, now + arcLen * 2, 1),
                Segment(self, now + arcLen * 2, now + arcLen * 3, 1),
            ]

            self.towers = [
                RainbowTower(self, now, self.segments[2], self.segments[0], now),
                RainbowTower(self, now + arcLen, self.segments[0], self.segments[1], now + arcLen/3),
                RainbowTower(self, now + arcLen * 2, self.segments[1], self.segments[2], now + (arcLen/3) * 2),
            ]

            self.explosionColor = Colors.WHITE
            self.collisionColor = [0xff, 0xff, 0xff]
            self.towerWidth = 50

        else: # default = "duel"
            self.segments = [
                    Segment(self, Clock.NORTH, Clock.HOUR_MARKS_POS_LIST[6], 3),
                    Segment(self, Clock.HOUR_MARKS_POS_LIST[6], Clock.NORTH, 3)
            ]
            self.towers = [
                    Tower(self, Clock.NORTH,                  self.segments[1], self.segments[0], [0xff, 0, 0]),
                    Tower(self, Clock.HOUR_MARKS_POS_LIST[6], self.segments[0], self.segments[1], [0, 0xff, 0]),
            ]
            self.explosionColor = [0xff, 0x80, 0x30]
            self.collisionColor = [0xff, 0xff, 0xff]
            self.towerWidth = 50

    def next(self):
        block = Modular.next(self)

        self.counter += 1

        # if self.counter % 100 == 2:
        #     self.segments[0].fire([0xff, 0, 0], 1)
        #     self.segments[0].fire([0, 0, 0xff], -1)

        for tower in self.towers:
            tower.paint(block)

        for segment in self.segments:
            segment.paint(block)

        return block

MODULES["cannon"] = Cannon