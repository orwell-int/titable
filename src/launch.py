import os, sys, io
import M5
from M5 import *
import table


TITABLE = None


def setup():
    global TITABLE
    M5.begin()
    Widgets.fillScreen(0x000000)
    TITABLE = table.Titable()


def loop():
    global TITABLE
    M5.update()
    if M5.Touch.getCount():
        TITABLE.touch(M5.Touch.getX(), M5.Touch.getY())


if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg

            print_error_msg(e)
        except ImportError:
            print("please update to latest firmware")
