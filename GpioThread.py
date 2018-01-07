import threading
import time

import sys

import Const
import Defs
from Const import *
from neopixel import Adafruit_NeoPixel

import DefaultComponents
import Filters
import Modules
import Transitions

class GpioThread (threading.Thread):

    KEYWORDS = ["help", "module", "filter", "transition", "update", "off", "?", "h", "m", "f", "t", "u"]

    def __init__(self):
        threading.Thread.__init__(self)

        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        self.strip.begin()

        self.exit = False
        self.command = None
        self.reply = None
        self.lock = threading.Condition()

        print("GpioThread initialized")

    def run(self):

        self.moduleFactory = DefaultComponents.ColorModule
        self.filterFactory = DefaultComponents.NoneFilter
        self.transitionFactory = DefaultComponents.NoneTransition

        self.moduleFactory.configure([])
        self.filterFactory.configure([])
        self.transitionFactory.configure([])

        self.module = self.filterFactory.getinstance(self.moduleFactory.getinstance())

        while True:
            self.lock.acquire()
            if self.exit:
                self.lock.release()
                break

            if self.command is not None:
                self.reply = self.processCommandT(self.command)
                self.command = None
                self.lock.notify()

            self.lock.release()

            block = self.module.next()
            self.project(block)

        print("GpioThread stopping")

        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, 0x0)
        self.strip.show()

    def processCommandT(self, line):
        """Apply the changes, ane return the reply to the command"""
        chunks = line.split()
        if len(chunks) <= 0:
            return "ERR: Empty command"
        if not chunks[0] in GpioThread.KEYWORDS:
            return "ERR: Unknown keyword {}; use \"help\" or \"?\" for references"

        if chunks[0] in ["help", "h", "?"]:
            if len(chunks) == 1:
                return self.getHelp()
            return self.getHelp(chunks[1:])

        if chunks[0] in ["update", "u"]:
            self.update(self.filterFactory.getinstance(self.moduleFactory.getinstance()))
            return "OK: Transition complete"

        if chunks[0] in ["module", "m"]:
            if len(chunks) < 2:
                return self.getHelp(["m"])
            module = Defs.MODULES.get(chunks[1])
            if module is None:
                return "ERR: unknown module \"{}\"".format(chunks[1])
            self.moduleFactory = module
            self.moduleFactory.configure(chunks[2:])
            return "OK: Module set to \"{}\"; use >> update << to apply changes".format(chunks[1])

        if chunks[0] in ["filter", "f"]:
            if len(chunks) < 2:
                return self.getHelp(["f"])
            factory = Defs.FILTERS.get(chunks[1])
            if factory is None:
                return "ERR: unknown filter \"{}\"".format(chunks[1])
            self.filterFactory = factory
            self.filterFactory.configure(chunks[2:])
            return "OK: Filter set to \"{}\"; use >> update << to apply changes".format(chunks[1])

        if chunks[0] in ["transition", "t"]:
            if len(chunks) < 2:
                return self.getHelp(["t"])
            transition = Defs.TRANSITIONS.get(chunks[1])
            if transition is None:
                return "ERR: unknown transition \"{}\"".format(chunks[1])
            self.transitionFactory = transition
            self.transitionFactory.configure(chunks[2:])
            return "OK: Transition set to \"{}\"; use >> update << to apply changes".format(chunks[1])

        if chunks[0] in ["off"]:
            Defs.MODULES.get("color").configure(["0x0"])
            self.update(Defs.MODULES.get("color").getinstance())
            # no filter used
            return "Strand off"

        return "TODO: Process commands"

    def update(self, afterModule):
        print("Starting transition")
        transition = self.transitionFactory.newinstance(self.module, afterModule)
        block = transition.next()
        while block is not None:
            self.project(block)
            block = transition.next()
        self.module = afterModule
        print("Transition finished")

    def getHelp(self, topic = []):
        if len(topic) > 0:
            if topic[0] in ["module", "m"]:
                if len(topic) > 1:
                    name = topic[1]
                    if name in Defs.MODULES.keys():
                        module = Defs.MODULES[name]
                        return Const.APP_NAME + " \"{}\":\n{}".format(module.name, module.help)
                    return Const.APP_NAME + " modules: Unknown name \"{}\"".format(name)
                return Const.APP_NAME + " modules: {}".format(Defs.MODULES.keys())

            if topic[0] in ["filter", "f"]:
                if len(topic) > 1:
                    name = topic[1]
                    if name in Defs.FILTERS.keys():
                        filter = Defs.FILTERS[name]
                        return Const.APP_NAME + " \"{}\":\n{}".format(filter.name, filter.help)
                    return Const.APP_NAME + " filters: Unknown name \"{}\"".format(name)
                return Const.APP_NAME + " filters: {}\n".format(Defs.FILTERS.keys())

            if topic[0] in ["transition", "t"]:
                if len(topic) > 1:
                    name = topic[1]
                    if name in Defs.TRANSITIONS.keys():
                        transition = Defs.TRANSITIONS[name]
                        return Const.APP_NAME + " \"{}\":\n{}".format(transition.name, transition.help)
                    return Const.APP_NAME + " transitions: Unknown name \"{}\"".format(name)
                return Const.APP_NAME + " transitions: {}\n".format(Defs.TRANSITIONS.keys())

        return Const.APP_NAME + " manual. The recognized keywords are\n" \
               "  module/m: graphics painter configuration\n" \
               "  filter/f: display filter configuration; filters are used to display only subsections of the graphics\n" \
               "  transition/t: configure transition used to update to new graphics module or filter\n" \
               "  update/u: execute the configuration changes\n" \
               "  off: turn the strand off (display black)\n" \
               "  help/h/?: display help. use >> help <keyword> << to list available configuration details\n"

    def ctrl(self, command):
        self.lock.acquire()
        self.command = command
        self.reply = None
        self.lock.wait()
        reply = self.reply
        if reply == None:
            print("M: Command \"{}\": no reply set!")
        self.lock.release()
        return reply

    def quit(self):
        self.lock.acquire()
        self.exit = True
        print("GpioThread signalled to stop")
        self.lock.release()

    def __adjust(self, num):
        return num * (num >> 2) >> 6
        # return num

    def __toGrbInt(self, tuple):
        ret = (self.__adjust(tuple[1]) << 16) \
              + (self.__adjust(tuple[0]) << 8) \
              + self.__adjust(tuple[2])
        return ret

    def project(self, block):
        # print("Graphics colors={}"
        #       .format(map(hex, map(lambda x: (x[0] << 16) + (x[1] << 8) + x[2], block))))
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, self.__toGrbInt(block[i]))
        self.strip.show()
        # colors = map(lambda x: self.strip.getPixelColor(x), range(LED_COUNT))

if __name__ == '__main__':
    t = GpioThread()
    t.start()

    for i in range(3):
        print("Main running for", i)
        time.sleep(1)
    t.quit()
    print("Waiting for Gpio to join")
    t.join(1)
    print("Gpio joined")
