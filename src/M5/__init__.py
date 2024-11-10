import sys


from . import Speaker

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
    pygame.display.update()
