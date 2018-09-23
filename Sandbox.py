import sys
import threading
from time import sleep

lock = threading.Condition()

class MyThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                print("Obtaining lock")
                lock.acquire()
                print("Lock acquired")
                lock.wait(1)
                print("Woke up")
                lock.release()
        except Exception:
            print("Raised exception{}".format(sys.exc_info()))


t = MyThread()
t.start()

sleep(5)

print("Main acquiring lock")
lock.acquire()
while True:
    print("Lock is being held")
    sleep(1)