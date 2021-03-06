import random

from Defs import *
import Const

class RainbowModule:
    name = "Running rainbow module"
    key = "rainbow"
    help = "Usage: >> module rainbow [speed=1] [single/triple]<<. \n" \
           "  Speed must be an integer - may be negative \n" \
           "  Mode is a string, default=triple"
    speed = 1
    cycles = 3

    @staticmethod
    def configure(args):
        if len(args) > 0:
            try:
                speed = int(args[0])
                RainbowModule.speed = speed
            except ValueError:
                RainbowModule.speed = 1
        if len(args) > 1:
            if (args[1] == "single"):
                RainbowModule.cycles = 1
            else:
                RainbowModule.cycles = 3



    @staticmethod
    def getinstance():
        return RainbowModule(RainbowModule.speed, RainbowModule.cycles)

    def __init__(self, speed, cycles):
        self.counter = 0
        self.speed = speed
        self.cycles = cycles

        if speed == 0:
            self.counter = random.randint(0, Const.LED_COUNT-1)
            self.hidden = 0

    def next(self):
        return self.rainbow()

    @staticmethod
    def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        # cycle is 306
        pos = pos % 306
        if pos < 102:
            return [pos * 2, 204 - pos * 2, 0]
        elif pos < 204:
            pos -= 102
            return [204 - pos * 2, 0, int(pos * 1.7)]
        else:
            pos -= 204
            return [0, pos * 2, int(172 - pos * 1.7)]

    def rainbow(self):
        """Draw rainbow that fades across all pixels at once."""

        # hidden feature of speed=0: makes one cycle per ~hour
        if self.speed == 0:
            self.hidden += 1
            if self.hidden > 336:
                self.counter += 1
                self.hidden = 0

        block = []
        if self.cycles == 3:
            for i in range(Const.LED_COUNT):
                block.append(RainbowModule.wheel((i + self.counter)))
            self.counter += self.speed
            while self.counter < 0:
                self.counter += 306
        else:
            for i in range(Const.LED_COUNT):
                block.append( RainbowModule.wheel((i + self.counter) / 3));
            self.counter += self.speed
            while self.counter < 0:
                self.counter += 918


        return block

class VertigoModule:
    name = "Color changing module"
    key = "vertigo"
    help = "Usage: >> module vertigo [speed=1] <<. Speed must be an integer"
    speed = 1
    MAX_VAL = 0xb0

    @staticmethod
    def configure(args):
        if len(args) > 0:
            try:
                speed = float(args[0])
                VertigoModule.speed = speed
            except ValueError:
                VertigoModule.speed = 1

    @staticmethod
    def getinstance():
        return VertigoModule(VertigoModule.speed)

    def __init__(self, speed):
        self.counter = random.randint(1, VertigoModule.MAX_VAL * 6)
        self.speed = speed
        print("Vertigo: speed={}".format(self.speed))

    @staticmethod
    def wheel(pos):
        MAX_VAL = VertigoModule.MAX_VAL

        pos = pos % (6*MAX_VAL)

        if pos < MAX_VAL:
            return [0, pos, MAX_VAL]
        pos -= MAX_VAL
        if pos < MAX_VAL:
            return [0, MAX_VAL, MAX_VAL-pos]
        pos -= MAX_VAL
        if pos < MAX_VAL:
            return [pos, MAX_VAL, 0]
        pos -= MAX_VAL
        if pos < MAX_VAL:
            return [MAX_VAL, MAX_VAL-pos, 0]
        pos -= MAX_VAL
        if pos < MAX_VAL:
            return [MAX_VAL, 0, pos]
        pos -= MAX_VAL
        return [MAX_VAL-pos, 0 , MAX_VAL]

    def next(self):
        color = VertigoModule.wheel(int(math.floor(self.counter)))
        block = map(lambda x: color[:], range(Const.LED_COUNT))
        self.counter = (self.counter + self.speed) % (VertigoModule.MAX_VAL * 6)
        return block

MODULES["rainbow"] = RainbowModule
MODULES["vertigo"] = VertigoModule
