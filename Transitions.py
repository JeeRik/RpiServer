from Defs import *
from DefaultComponents import ColorModule
import Const

class BlendTransition:
    name = "Blending transition"
    key = "blend"
    help = "usage: >>transition blend [length=16]<<, where length is the number of frames the blending takes"

    length = 16

    @staticmethod
    def configure(args):
        if len(args) > 0:
            length = 16
            try:
                length = int(args[0])
            except ValueError:
                length = 16
            BlendTransition.length = length
    @staticmethod
    def newinstance(beforeModule, afterModule):
        return BlendTransition(beforeModule, afterModule, BlendTransition.length)

    def __init__(self, beforeModule, afterModule, length):
        self.beforeModule = beforeModule
        self.afterModule = afterModule
        self.length = length
        self.taken = 0

    def __blend(self, c1, c2, ratio):
        return map(lambda x,y: (x*(256-ratio) + y*ratio) >> 8, c1, c2)

    def next(self):
        if (self.length <= self.taken): return None
        phase = (self.taken<<8) / self.length

        before = self.beforeModule.next()
        after = self.afterModule.next()

        ret = []

        for i in range(Const.LED_COUNT):
            ret.append(self.__blend(before[i], after[i], phase))

        self.taken += 1
        return ret

class WrapTransition:
    name = "Wrap transition"
    key = "wrap"
    help = "usage: >>transition wrap [start=window] [speed=3]<<, \n" \
           "  start is pixel ID of the pixel to wrap from:\n" \
           "      pre-defined options: window, door\n" \
           "  speed is the number of pixels per frame added"

    POSITIONS={}
    POSITIONS["door"] = (Const.LED_COUNT + Const.LED_CORNERS[3])/2
    POSITIONS["window"] = (Const.LED_CORNERS[1] + Const.LED_CORNERS[2]) / 2

    start = POSITIONS["door"]
    speed = 3

    @staticmethod
    def configure(args):
        if len(args) > 0:
            start = 3
            try:
                if args[0] in WrapTransition.POSITIONS.keys():
                    start = WrapTransition.POSITIONS[args[0]]
                else:
                    start = int(args[0])
            except ValueError:
                start = WrapTransition.POSITIONS["window"]
            WrapTransition.start = start

        if len(args) > 1:
            try:
                speed = int(args[1])
            except ValueError:
                speed = 3
            WrapTransition.speed = speed

    @staticmethod
    def newinstance(beforeModule, afterModule):
        return WrapTransition(beforeModule, afterModule, WrapTransition.start, WrapTransition.speed)

    def __init__(self, beforeModule, afterModule, start, speed):
        self.beforeModule = beforeModule
        self.afterModule = afterModule
        self.start = start
        self.speed = speed
        self.complete = 0

    def __isNewId(self, id, fromId, toId):
        return (id >= fromId and id <= toId) \
                if fromId <= toId else \
                (id >= fromId or id <= toId)

    def next(self):
        if ((self.complete << 1) >= Const.LED_COUNT): return None

        before = self.beforeModule.next()
        after = self.afterModule.next()

        fromId = self.start - self.complete
        toId = self.start + self.complete
        if fromId < 0: fromId = fromId + Const.LED_COUNT
        if toId >= Const.LED_COUNT: toId -= Const.LED_COUNT

        s = ""
        for x in map(lambda x: "+" if self.__isNewId(x, fromId, toId) else "-", range(918)):
            s += x

        ret = map(
            lambda x, y, z: y if self.__isNewId(z, fromId, toId) else x,
            before,
            after,
            range(Const.LED_COUNT))

        self.complete += self.speed
        return ret

class PopTransition:
    name = "Dim&Pop transition"
    key = "pop"
    help = "usage: >>transition pop [length=16]<<, where length is the number of frames dim and then take"
    length = 16

    @staticmethod
    def configure(args):
        if len(args) > 0:
            length = 16
            try:
                length = int(args[0])
            except ValueError:
                length = 16
            PopTransition.length = length

    @staticmethod
    def newinstance(beforeModule, afterModule):
        return PopTransition(beforeModule, afterModule, PopTransition.length)

    def __init__(self, beforeModule, afterModule, length):
        self.beforeModule = beforeModule
        self.afterModule = afterModule
        self.length = length
        self.black = ColorModule([0,0,0])
        self.dimTransition = BlendTransition(beforeModule, self.black, length)
        self.popTransition = BlendTransition(self.black, afterModule, length)
        self.stage = 0
        self.stage2Delay = length/2

    def next(self):
        if self.stage == 0:
            block = self.dimTransition.next()
            if block is not None:
                return block
            self.stage = 1
        if self.stage == 1:
            if (self.stage2Delay > 0) > 0:
                self.stage2Delay -= 1
                return self.black.next()
            self.stage = 2
        if self.stage == 2:
            block = self.popTransition.next()
            if block is not None:
                return block
            self.stage = 3
        return None

TRANSITIONS["blend"] = BlendTransition
TRANSITIONS["wrap"] = WrapTransition
TRANSITIONS["pop"] = PopTransition