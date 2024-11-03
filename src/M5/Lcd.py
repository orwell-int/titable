from . import Widgets
import M5
import colours

import pygame
import pygame.freetype


FONT = 0
TEXT_COLOUR = None
TEXT_BACKGROUND_COLOUR = None

PYGAME_FONT = None


def setFont(index: int):
    global FONT
    global PYGAME_FONT
    FONT = index
    if index == 2:
        PYGAME_FONT = pygame.freetype.SysFont("DejaVuSans-ExtraLight.ttf", 12)
    elif index == 3:
        PYGAME_FONT = pygame.freetype.SysFont("DejaVuSans-ExtraLight.ttf", 18)


def textWidth(text: str) -> int:
    return 0


def fontHeight() -> int:
    global FONT
    if Widgets.FONTS.DejaVu18 == FONT:
        return 18
    else:
        # not implemented
        return 0


def setTextColor(text_colour_hexa: int, fill_colour_hexa: int):
    global TEXT_COLOUR
    global TEXT_BACKGROUND_COLOUR
    TEXT_COLOUR = text_colour_hexa
    TEXT_BACKGROUND_COLOUR = fill_colour_hexa
    pass


def drawString(text: str, tx: int, ty: int):
    global PYGAME_FONT
    global TEXT_COLOUR
    if PYGAME_FONT is None:
        PYGAME_FONT = pygame.freetype.SysFont("DejaVuSans-ExtraLight.ttf", 18)
    text_surface, rectangle = PYGAME_FONT.render(text, colours.rgb(TEXT_COLOUR))
    _, _, dx, dy = rectangle
    M5.DISPLAY.blit(text_surface, (tx - dx // 2, ty - dy // 2))


def drawRect(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pygame.draw.rect(
        M5.DISPLAY, colours.rgb(colour_hexa), pygame.Rect(tx, ty, dx, dy), 1
    )
    pass


def fillRect(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pygame.draw.rect(M5.DISPLAY, colours.rgb(colour_hexa), pygame.Rect(tx, ty, dx, dy))
    pass
