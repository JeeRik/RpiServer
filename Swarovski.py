import datetime
import random
import numpy as np

import Defs
from Defs import *
import Const

class Clock:
    NORTH = (Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2
    HOUR_MARKS_POS_LIST = map(
        lambda x: Defs.adjustToLedRange(
            int( math.floor(
                ((Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2)
                - ( Const.LED_COUNT/12.0 * x) ))),
            range(12))
    MINUTE_MARKS_POS_LIST =  map(
        lambda x: Defs.adjustToLedRange(
            int( math.floor(
                ((Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2)
                - ( Const.LED_COUNT/60.0 * x) ))),
            range(60))
    # @staticmethod
    # def getMinuteMarksPosList():
    #     diff = Const.LED_COUNT / 60.0
    #     north = (Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2
    #     posList = map(lambda x: Defs.adjustToLedRange( int( math.floor( north - (diff*x) ))), range(60))
    #     return posList

    @staticmethod
    def getHourNeedlePos():
        now = datetime.datetime.now()
        arc = ((Const.LED_COUNT * (now.second + now.minute*60 + now.hour*3600)) / 43200)
        pos = (Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2
        pos -= arc
        while pos < 0:
            pos += Const.LED_COUNT
        return pos
    @staticmethod
    def getMinuteNeedlePos():
        now = datetime.datetime.now()
        arc = ((Const.LED_COUNT * (now.second + now.minute*60)) / 3600)
        pos = (Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2
        pos -= arc
        if pos < 0:
            pos += Const.LED_COUNT
        return pos
    @staticmethod
    def getSecondNeedlePos():
        now = datetime.datetime.now()
        arc = ((Const.LED_COUNT * (now.microsecond + now.second*1000000)) / 60000000.0)
        pos = (Const.LED_CORNERS[3] + Const.LED_CORNERS[0] + Const.LED_COUNT) / 2
        pos -= int(math.floor(arc))
        if pos < 0:
            pos += Const.LED_COUNT
        return pos

    name = "Clock. Analog-ish."
    key = "clock"
    help = "Usage: >> module clock <<"

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance():
        return Clock()

    def __init__(self):
        None

    def next(self):
        block = map(lambda x: [0,0x10,0x10][:], range(Const.LED_COUNT))

        for pos in Clock.MINUTE_MARKS_POS_LIST:
            block[pos] = [0x60, 0x60, 0]
        for pos in Clock.HOUR_MARKS_POS_LIST:
            block[pos] = [0x30, 0x60, 0x80]
        sec = Clock.getSecondNeedlePos()
        block[sec] = Colors.addColors(block[sec], [0x60, 0x40, 0])
        block[(sec+1) % Const.LED_COUNT] = Colors.addColors(block[(sec+1) % Const.LED_COUNT], [0x60, 0x40, 0])
        minute = Clock.getMinuteNeedlePos()
        block[minute] = Colors.addColors(block[minute], [0xff, 0xff, 0])
        block[(minute+1) % Const.LED_COUNT] = Colors.addColors(block[(minute+1) % Const.LED_COUNT], [0xff, 0xb0, 0])
        hour = Clock.getHourNeedlePos()
        block[hour] = Colors.addColors(block[hour], [0, 0, 0xff])
        block[(hour+1) % Const.LED_COUNT] = Colors.addColors(block[(hour+1) % Const.LED_COUNT], [0, 0, 0xff])

        return block

class Swarovski:
    name = "Swarovski garden-inspired theme"
    key = "swarovski"
    help = "Usage: >> module swarovski <<"

    spaceDistributionBase = 25000
    timeDistributionBase = 200
    timeDistributionRange = 20
    durationDistributionBase = 200
    durationDistributionRange = 60

    skyColor = [0,0,0x0]
    sunColor = [0xff, 0xb0, 0x48]
    sunRadius = 100

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance():
        return Swarovski()

    @staticmethod
    def getShineColor():
        while True:
            color = map(lambda x: random.randint(0, 0xff), ['r', 'g', 'b'])
            if any(map(lambda x: x > 0xb0, color)):
                color[1] = int(math.floor(color[1] / 1.1))
                color[2] = int(math.floor(color[2] / 1.3))
                return color

    @staticmethod
    def getShinePosition():
        pos = (np.random.poisson(Swarovski.spaceDistributionBase) - Swarovski.spaceDistributionBase)
        pos += Clock.getMinuteNeedlePos()
        pos += Const.LED_COUNT / 2
        pos %= Const.LED_COUNT
        return pos

    @staticmethod
    def getShineDuration():
        return (np.random.poisson(Swarovski.durationDistributionBase) - Swarovski.durationDistributionBase + Swarovski.durationDistributionRange/2) % Swarovski.durationDistributionRange

    @staticmethod
    def getNextShineDelay():
        delay = np.random.poisson(Swarovski.timeDistributionBase) - Swarovski.timeDistributionBase + Swarovski.timeDistributionRange/2
        return delay % Swarovski.timeDistributionRange

    def __init__(self):
        self.shines = [] # element form: [color, pos, timeLeft]
        self.timeToNextShine = 0

    def next(self):
        block = map(lambda x: self.skyColor[:], range(Const.LED_COUNT))

        # draw sun
        sunPos = Clock.getMinuteNeedlePos()
        Colors.putGradient(block, sunPos - self.sunRadius, sunPos, self.skyColor, self.sunColor)
        Colors.putGradient(block, sunPos, sunPos + self.sunRadius, self.sunColor, self.skyColor)

        # update shines
        self.timeToNextShine -= 1
        if self.timeToNextShine <= 0:
            self.shines.append([self.getShineColor(), self.getShinePosition(), self.getShineDuration()])
            self.shines = filter(lambda x: x[2] > 0, self.shines)
            self.timeToNextShine = self.getNextShineDelay()

        # draw shines
        for shine in self.shines:
            if shine[2] > 0:
                block[shine[1]] = shine[0][:]
            shine[2] = shine[2] - 1

        return block
        #return map(lambda x: x[:], self.spaceDistribution)#colorPaletteDemo)

MODULES["clock"] = Clock
MODULES["swarovski"] = Swarovski
