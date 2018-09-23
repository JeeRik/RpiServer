import datetime
import random
import numpy as np

import Defs
from Defs import *
import Const
from Swarovski import Swarovski


class Fireworks:
    name = "Fireworsk show"
    key = "fireworks"
    help = "Usage >> m fireworks <<. No more options. Just sit and enjoy"

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance():
        return Fireworks()

    @staticmethod
    def addFlash(block, flash):
        """Flash parameters: [position, color, current dim ratio, dim ratio increment, current width, width increment]"""
        maxColor = Colors.dim(flash[1], int(math.floor(flash[2])))

        Colors.addGradient(block, int(math.floor(flash[0] - flash[4])), flash[0], [0, 0, 0], maxColor)
        Colors.addGradient(block, flash[0], int(math.floor(flash[0] + flash[4])), maxColor, [0, 0, 0])

        flash[2] = flash[2] + flash[3]
        flash[4] = flash[4] + flash[5]

    @staticmethod
    def filterFlashes(flashes):
        return filter(lambda x: x[2] <= 0xff, flashes)

    def __init__(self):
        self.flashes = []
        self.timeToNextFlash = 0

        self.lastFlashPos = 0

    def getBackground(self):
        return map(lambda x: [0,0,0][:], range(Const.LED_COUNT))

    def getNextFlashColor(self):
        return Swarovski.getShineColor()

    def getNextFlashPos(self):
        self.lastFlashPos = (self.lastFlashPos + np.random.poisson(int(math.floor(6.33*Const.LED_COUNT)))) % Const.LED_COUNT
        return self.lastFlashPos

    def getNextFlashDelay(self):
        delay = abs(np.random.poisson(100) - 100)

        return delay

    def getNextFlash(self):
        ret = []
        ret.append(self.getNextFlashPos()) # position
        ret.append(self.getNextFlashColor()) # color
        ret.append(0) # current dim ratio
        ret.append(random.uniform(5,8)) # dim ratio increment
        ret.append(1) # current width
        ret.append(random.randint(2,4)) # width increment

        return ret

    def next(self):
        block = self.getBackground()

        self.timeToNextFlash -= 1
        if self.timeToNextFlash <= 0:
            self.timeToNextFlash = self.getNextFlashDelay()
            self.flashes.append(self.getNextFlash())
            self.flashes = Fireworks.filterFlashes(self.flashes)


        for flash in self.flashes:
            Fireworks.addFlash(block, flash)
            # maxColor = Colors.dim(flash[1], int(math.floor(flash[2])))
            #
            # Colors.addGradient(block, int(math.floor(flash[0] - flash[4])), flash[0], [0,0,0], maxColor)
            # Colors.addGradient(block, flash[0], int(math.floor(flash[0] + flash[4])), maxColor, [0,0,0])
            #
            #
            # flash[2] = flash[2] + flash[3]
            # flash[4] = flash[4] + flash[5]

        return block

class Fireplace(Fireworks):
    name = "Running rainbow module"
    key = "rainbow"
    help = "Usage: >> module fireplace <<"

    BG_COLOR = [0x50, 0x2c, 0]
    FLASH_COLORS = [
        [0xff, 0x60, 0],
        [0xff, 0xb0, 0],
        [0xff, 0x80, 0x40]
    ]

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance():
        return Fireplace()

    def getBackground(self):
        return map(lambda x: Fireplace.BG_COLOR[:], range(Const.LED_COUNT))

    def getNextFlashColor(self):
        return self.FLASH_COLORS[random.randint(0, len(self.FLASH_COLORS) - 1)]

    def getNextFlashDelay(self):
        return int(math.floor(Fireworks.getNextFlashDelay(self) * 0.5))

    def getNextFlash(self):
        ret = []
        ret.append(self.getNextFlashPos()) # position
        ret.append(self.getNextFlashColor()) # color
        ret.append(0) # current dim ratio
        ret.append(random.uniform(2,4)) # dim ratio increment
        ret.append(1) # current width
        ret.append(random.uniform(0.5, 2)) # width increment

        return ret


MODULES["fireworks"] = Fireworks
MODULES["fireplace"] = Fireplace
