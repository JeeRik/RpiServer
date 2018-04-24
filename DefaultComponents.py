import copy

import Const
from Defs import *

class ColorModule:
    name = "Colors Module"
    key = "color"
    help = "Color Module creates a single-color modules:\n" \
           "  usage: >> module color [color=blue] <<\n" \
           "  colors may be:\n" \
           "    {}\n" \
           "    or \'0xRRGGBB\', where red/green/blue range 00 to ff".format(Colors.colormap.keys())

    """RGB color to be used"""

    @staticmethod
    def configure(args):
        if len(args) == 0:
            ColorModule.color = [0,0,0]
            print("Default color set to 0x0")
            return
        try:
            color = Colors.decode(args[0])
            ColorModule.color = color
        except ValueError:
            return "ERR: Unknown color \"{}\"".format(args[0])

    @staticmethod
    def getinstance():
        return ColorModule(ColorModule.color)

    def __init__(self, color):
        self.color = color

    def next(self):
        ret = []
        for i in range(Const.LED_COUNT):
            ret.append(self.color[:])
        return ret

class NoneFilter:
    name = "None filter"
    key = "none"
    help = "  usage: >> filter none <<. Displays module graphics as-is"

    dim = 0

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def getinstance(module):
        return module

class NoneTransition:
    name = "No transition"
    key = "none"
    help = "usage: >> transition none <<. Instantly changes graphics module"

    @staticmethod
    def configure(args):
        None

    @staticmethod
    def newinstance(beforeModule, afterModule):
        return NoneTransition()

    def next(self):
        return None


MODULES["color"] = ColorModule
TRANSITIONS["none"] = NoneTransition
FILTERS["none"] = NoneFilter
