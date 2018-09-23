import math
import numbers

import Const

MODULES = dict()
TRANSITIONS = dict()
FILTERS = dict()

class Colors:
    BLACK = [0,0,0]
    WHITE = [0x80, 0x80, 0x80]

    colormap = dict()
    """colormap is a mapping from string to RGB values"""
    colormap["black"] = 0x0
    colormap["blue"] = 0xb0
    colormap["red"] = 0xb00000
    colormap["green"] = 0xb000
    colormap["white"] = 0x808080
    colormap["cyan"] = 0xb0b0
    colormap["magenta"] = 0xb000b0
    colormap["yellow"] = 0xb0b000


    @staticmethod
    def decode(color):

        if isinstance(color, basestring):
            if color in Colors.colormap.keys():
                color = Colors.colormap[color]
            else:
                color = int(color, 0)

        return [color >> 16, (color >> 8) & 255, color & 255]

    @staticmethod
    def dim(color, rate):
        rate = 256 - rate
        return map(lambda y: ((y * rate) >> 8), color)
    @staticmethod
    def addColors(c1, c2):
        return [max(c1[0], c2[0]), max(c1[1], c2[1]), max(c1[2], c2[2])]

    @staticmethod
    def putGradient(block, pos1, pos2, c1, c2):
        if pos2 <= pos1:
            pos2 += Const.LED_COUNT

        len = pos2 - pos1

        r = c1[0] * len
        g = c1[1] * len
        b = c1[2] * len

        rdiff = c2[0] - c1[0]
        gdiff = c2[1] - c1[1]
        bdiff = c2[2] - c1[2]

        for i in range(len+1): # paint includes the pos2 pixel
            block[(pos1 + i) % Const.LED_COUNT] = [ (r + rdiff * i) / len , (g + gdiff * i) / len,(b + bdiff * i) / len]

    @staticmethod
    def addGradient(block, pos1, pos2, c1, c2):
        pos1 = pos1 % Const.LED_COUNT
        pos2 = pos2 % Const.LED_COUNT

        if pos2 <= pos1:
            pos2 += Const.LED_COUNT

        len = pos2 - pos1

        r = c1[0] * len
        g = c1[1] * len
        b = c1[2] * len

        rdiff = c2[0] - c1[0]
        gdiff = c2[1] - c1[1]
        bdiff = c2[2] - c1[2]

        for i in range(len+1): # paint includes the pos2 pixel
            pos = (pos1 + i) % Const.LED_COUNT
            block[pos] = [
                max((r + rdiff * i)  / len, block[pos][0]),
                max((g + gdiff * i) / len, block[pos][1]),
                max((b + bdiff * i) / len, block[pos][2])]

def adjustToLedRange(pos):
    if pos < 0:
        while pos < 0:
            pos += Const.LED_COUNT
        return pos
    while pos >= Const.LED_COUNT:
        pos -= Const.LED_COUNT
    return pos