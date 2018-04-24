from Defs import *
import Const

class DoorFilter:
    name = "Door area filter"
    key = "door"
    help = "No options. Sorry"

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance(module):
        return HideFilter(64, Const.LED_CORNERS[3]-64, 64, module)

class WindowFilter:
    name = "Window area filter"
    key = "window"
    help = "No options. Sorry"

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance(module):
        return HideFilter(Const.LED_CORNERS[2]+64, Const.LED_CORNERS[1]-64, 64, module)


class HideFilter:
    name = "Hide filter"
    key = "hide"
    help = "  usage: >> filter hide <start> <end> [<fade=64>]\n" \
           "    replace the section start-end with black. Blackening further extends for <fade> pixels on both sides with a gradient"

    def __init__(self, start, end, fade, module):
        self.start = start
        self.end = Const.LED_COUNT + end if end < start else end
        self.fade = fade
        self.module = module

    def next(self):
        block = self.module.next()

        for i in range(self.end - self.start % Const.LED_COUNT):
            block[(self.start + i) % Const.LED_COUNT] = [0,0,0]

        step = (256 / self.fade)

        for idPos, idNeg, dim in zip(
                range(self.start, self.start - self.fade, -1),
                range(self.end,   self.end + self.fade, 1),
                range(256, 0, -step)):
            block[idPos % Const.LED_COUNT] = Colors.dim(block[idPos % Const.LED_COUNT], dim)
            block[idNeg % Const.LED_COUNT] = Colors.dim(block[idNeg % Const.LED_COUNT], dim)

        return block

class DimFilter:
    name = "Dim filter"
    key = "dim"
    help = "  usage: >> filter dim [rate=0] <<, where rate ranges 0-transparetnt to 255-dark"

    dim = 0

    @staticmethod
    def configure(args):
        dim = 0
        if len(args) == 0:
            None
        else:
            try:
                dim = int(args[0])
            except ValueError:
                dim = 0
            dim = int(args[0], 0)
            if dim < 0: dim = 0
            if dim > 255: dim = 255
        DimFilter.dim = dim

    @staticmethod
    def getinstance(module):
        return DimFilter(module, DimFilter.dim)

    def __init__(self, module, dim):
        self.module = module
        self.dim = dim

    def next(self):
        block = self.module.next()
        if self.dim == 0:
            return block
        dim = 256 - self.dim
        return map(lambda x: map(lambda y: ((y * dim) >> 8), x), block)

class TheatreFilter:
    speed = 1
    offCount = 4
    sampleLen = 10

    @staticmethod
    def configure(args):
        speed = 1
        if len(args) > 0:
            try:
                speed = int(args[0])
            except ValueError:
                speed = 1
        if speed == 0:
            speed = 1

        absSpeed = speed if speed >= 0 else -speed

        onPixels = 4 * absSpeed
        offPixels = 6 * absSpeed
        if (len(args) > 2):
            try:
                onPixels = int(args[1])
                offPixels = int(args[2])
            except ValueError:
                onPixels = 4 * absSpeed
                offPixels = 6 * absSpeed

        TheatreFilter.speed = speed
        TheatreFilter.offCount = offPixels
        TheatreFilter.sampleLen = onPixels + offPixels

    def __init__(self, module, sections):
        self.module = module
        self.counter = 0

        self.sections = []
        for section in sections:
            dir = -1 if section[2] < 0 else 1
            end = section[1] if (section[1] - section[0]) * dir > 0 else section[1] + Const.LED_COUNT * dir # end of block, adjusted so that end is in the right direction from start
            if end == section[0]: end -= Const.LED_COUNT
            length = (end - section[0]) * dir

            self.sections.append([
                section[0], # start of block
                end,
                section[2] if section[2] >= 0 else -section[2], # speed
                section[3], # offcount
                section[4], # sample length
                section[5] if len(section) > 5 else 0, # offset
                dir,
                length]) #direction at [6]

        print("New TheatreFilter: {}".format(self.sections))

    def next(self):
        block = self.module.next()
        counter = self.counter

        for section in self.sections:
            # anchor = (self.counter * section[2] + section[5] + section[0]) % section[4]
            # for i in range(section[0], section[1], 1):
            #     if (i+anchor) % section[4] < section[3]:
            #         block[i % Const.LED_COUNT] = [0,0,0]
            for i in range(section[7]+1):
                if ((i + counter*section[2]) % section[4]) < section[3]:
                    block[(i*section[6] + section[0]) % Const.LED_COUNT] = [0,0,0]

        self.counter += 1
        return block

class ChaseFilter:
    name = "Chase filter"
    key = "chase"
    help = ">>> filter chase <speed> <onPixels=speed*6> <offPixels=speed*4>"

    @staticmethod
    def configure(args):
        TheatreFilter.configure(args)

    @staticmethod
    def getinstance(module):
        return TheatreFilter(module, [[0,Const.LED_COUNT,TheatreFilter.speed, TheatreFilter.offCount, TheatreFilter.sampleLen]])

class ArrowFilter:

    name = "Arrow filter"
    key = "arrow"
    help = "usage: >>filter arrow [speed=1]<<"

    speed = 1

    @staticmethod
    def configure(args):
        TheatreFilter.configure(args)

    @staticmethod
    def getinstance(module):
        door = (Const.LED_CORNERS[3] + Const.LED_COUNT) / 2
        window = (Const.LED_CORNERS[1] + Const.LED_CORNERS[2]) / 2
        absSpeed = ArrowFilter.speed
        if absSpeed < 0:
            absSpeed = -absSpeed
        sections = [
                [door, window, TheatreFilter.speed, TheatreFilter.offCount, TheatreFilter.sampleLen],
                [door, window, -TheatreFilter.speed, TheatreFilter.offCount, TheatreFilter.sampleLen]
        ]
        return TheatreFilter(module, sections)

class GazeFilter:
    name = "Gaze filter"
    key = "gaze"
    help = "usage: >>filter gaze [speed=1]<<"

    speed = 1

    @staticmethod
    def configure(args):
        TheatreFilter.configure(args)

    @staticmethod
    def getinstance(module):
        door = (Const.LED_CORNERS[3] + Const.LED_COUNT) / 2
        window = (Const.LED_CORNERS[1] + Const.LED_CORNERS[2]) / 2
        left = (Const.LED_CORNERS[2] + Const.LED_CORNERS[3]) / 2
        right = (Const.LED_CORNERS[0] + Const.LED_CORNERS[1]) / 2

        absSpeed = GazeFilter.speed
        if absSpeed < 0:
            absSpeed = -absSpeed

        sections = [
            [Const.LED_CORNERS[0], right],
            [Const.LED_CORNERS[1], right],
            [Const.LED_CORNERS[1], window],
            [Const.LED_CORNERS[2], window],
            [Const.LED_CORNERS[2], left],
            [Const.LED_CORNERS[3], left],
            [Const.LED_CORNERS[3], door],
            [Const.LED_COUNT, door],
        ]

        sections = map(lambda x, y: [x[0], x[1], TheatreFilter.speed * (-1) * ((-1)**y), TheatreFilter.offCount, TheatreFilter.sampleLen], sections, range(len(sections)))
        return TheatreFilter(module, sections)

class SonarFilter:
    name = "Sonar filter"
    key = "sonar"
    help = "usage: >>filter sonar [speed=4 width=100 tail=200]<<"

    speed = 4
    width = 10
    tail = 64

    @staticmethod
    def configure(args):
        if len(args) > 0:
            speed = 4
            try:
                speed = int(args[0])
            except ValueError:
                speed = 4
            SonarFilter.speed = speed
        if len(args) > 1:
            width = 100
            try:
                width = int(args[1])
            except ValueError:
                width = 100
            SonarFilter.width = width
        if len(args) > 2:
            tail = width*2
            try:
                tail = int(args[2])
            except ValueError:
                tail = width*2
            SonarFilter.tail = tail

    @staticmethod
    def getinstance(module):
        return SonarFilter(module, SonarFilter.speed, SonarFilter.width, SonarFilter.tail)

    def __init__(self, module, speed, width, tail):
        self.module = module
        self.speed = speed
        self.orientation = 1 if speed >= 0 else -1
        self.dimArgument = 256 / tail
        if 256 % tail > 0: self.dimArgument += 1
        self.dimArgument = self.dimArgument
        self.tail = (256 / self.dimArgument) * self.orientation
        self.width = width * self.orientation + self.tail
        self.pos = 0

        print("Input: s={} w={} t={}".format(speed, width, tail))
        print("Config: w={} s={} o={} d={} t={}".format(self.width, self.speed, self.orientation, self.dimArgument, self.tail))

    def next(self):
        block = self.module.next()

        start = self.pos + self.width
        stop = self.pos + Const.LED_COUNT*self.orientation
        step = self.orientation

        # print("Hide: {}->{}:{}".format(start,stop,step))
        for i in range(start, stop, step):
            block[i % Const.LED_COUNT] = [0,0,0]

        # print("Dim: {} {} {} {} {} {}".format(0, 256, self.dimArgument, self.pos, self.pos + self.tail, self.orientation))
        for i, j in zip(range(256, 0, -self.dimArgument), range(self.pos, self.pos + self.tail, self.orientation)):
            block[j % Const.LED_COUNT] = Colors.dim(block[j % Const.LED_COUNT], i)

        self.pos += self.speed
        return block


FILTERS["dim"] = DimFilter
FILTERS["door"] = DoorFilter
FILTERS["window"] = WindowFilter
FILTERS["chase"] = ChaseFilter
FILTERS["arrow"] = ArrowFilter
FILTERS["gaze"] = GazeFilter
FILTERS["sonar"] = SonarFilter