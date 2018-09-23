import math

import numpy as np
import random

import Const


class Graphic:
    def paint(self, block):
        raise NotImplementedError("Most override paint(block) in Graphic children")
    def hasNext(self):
        raise NotImplementedError("Most override hasNext() in Graphic children")

class Modular:

    def __init__(self):
        self.graphics = []
        self.lastPos = random.randint(0, Const.LED_COUNT)

    def getBackground(self):
        return map(lambda x: [0,0,0][:], range(Const.LED_COUNT))
    def getRandomPos(self):
        self.lastPos = (self.lastPos + np.random.poisson(6*Const.LED_COUNT) + (Const.LED_COUNT / 2)) % Const.LED_COUNT
        return self.lastPos

    def next(self):
        block = self.getBackground()

        for g in self.graphics:
            g.paint(block)

        self.graphics = filter(lambda x: x.hasNext(), self.graphics)

        return block