import math
import numbers

MODULES = dict()
TRANSITIONS = dict()
FILTERS = dict()

class Colors:
    colormap = dict()
    """colormap is a mapping from string to RGB values"""
    colormap["black"] = 0x0
    colormap["blue"] = 0xb0
    colormap["red"] = 0xb00000
    colormap["green"] = 0xb000
    colormap["white"] = 0x808080

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
