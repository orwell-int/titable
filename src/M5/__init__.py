import sys


from . import Speaker

import pygame


DISAPLAY = None
CLOCK = None


def begin():
    global DISPLAY
    global CLOCK
    Speaker.init()
    pygame.init()
    DISPLAY = pygame.display.set_mode((320, 240), 0, 32)
    CLOCK = pygame.time.Clock()
    pass


def update():
    global CLOCK
    while True:
        CLOCK.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            pygame.display.update()
