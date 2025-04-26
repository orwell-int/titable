import sys


from . import Speaker
from . import Lcd

import pygame


DISPLAY = None
CLOCK = None
TITABLE = None


def begin():
    global DISPLAY
    global CLOCK
    Speaker.init()
    pygame.init()
    DISPLAY = pygame.display.set_mode((320, 240), 0, 32)
    CLOCK = pygame.time.Clock()
    Lcd.initFonts()
    pass


def update():
    global TITABLE
    global CLOCK
    CLOCK.tick(30)
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if 1 == event.button:
            # left button
            x, y = pygame.mouse.get_pos()
            if TITABLE is not None:
                TITABLE.touch(x, y)
    elif event.type == pygame.MOUSEBUTTONUP:
        if 1 == event.button:
            # left button
            if TITABLE is not None:
                TITABLE.touch(None, None)
    pygame.display.update()
