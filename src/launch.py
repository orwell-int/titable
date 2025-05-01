import os, sys, io
import time
import M5
from M5 import *
import table
import device


TITABLE = None


def setup():
    global TITABLE
    M5.begin()
    Widgets.fillScreen(0x000000)
    if device.is_micropython():
        leds_only_print = False
        Speaker.setVolume(15)
    else:
        leds_only_print = True
    TITABLE = table.Titable(leds_only_print, num_players=0)
    if M5.Touch.getCount():
        time.sleep(1)
    if M5.Touch.getCount():
        time.sleep(1)


def loop():
    global TITABLE
    M5.update()
    if M5.Touch.getCount():
        TITABLE.touch(M5.Touch.getX(), M5.Touch.getY())
    else:
        TITABLE.touch(None, None)


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
