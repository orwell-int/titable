from . import Widgets
import M5
import colours

import pygame
import pygame.freetype


FONT = 0
TEXT_COLOUR = None
TEXT_BACKGROUND_COLOUR = None

PYGAME_FONT = None


# the text is not long enough
# FONT_STRING = "DejaVuSans-ExtraLight.ttf"
# this is still not long enough, but a bit better
FONT_STRING = "DejaVuSans-Bold.ttf"


def setFont(index: int):
    global FONT
    global PYGAME_FONT
    FONT = index
    if Widgets.FONTS.DejaVu9 == FONT:
        PYGAME_FONT = pygame.freetype.SysFont(FONT_STRING, 9)
    elif Widgets.FONTS.DejaVu12 == FONT:
        PYGAME_FONT = pygame.freetype.SysFont(FONT_STRING, 12)
    elif Widgets.FONTS.DejaVu18 == FONT:
        PYGAME_FONT = pygame.freetype.SysFont(FONT_STRING, 18)
    elif Widgets.FONTS.DejaVu24 == FONT:
        PYGAME_FONT = pygame.freetype.SysFont(FONT_STRING, 24)
    elif Widgets.FONTS.DejaVu40 == FONT:
        PYGAME_FONT = pygame.freetype.SysFont(FONT_STRING, 40)


def _setDefaultFont():
    global PYGAME_FONT
    if PYGAME_FONT is None:
        setFont(Widgets.FONTS.DejaVu18)


def textWidth(text: str) -> int:
    global PYGAME_FONT
    _setDefaultFont()
    text_surface, rectangle = PYGAME_FONT.render(text)
    return rectangle[2]


def fontHeight() -> int:
    global FONT
    if Widgets.FONTS.DejaVu9 == FONT:
        return 9
    elif Widgets.FONTS.DejaVu12 == FONT:
        return 12
    elif Widgets.FONTS.DejaVu18 == FONT:
        return 18
    elif Widgets.FONTS.DejaVu24 == FONT:
        return 24
    elif Widgets.FONTS.DejaVu40 == FONT:
        return 40
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
    _setDefaultFont()
    PYGAME_FONT.render_to(M5.DISPLAY, (tx, ty), text, colours.rgb(TEXT_COLOUR))


def drawLine(x1: int, y1: int, x2: int, y2: int, colour_hexa: int):
    pygame.draw.line(M5.DISPLAY, colour_hexa, [x1, y1], [x2, y2])


def drawRect(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pygame.draw.rect(
        M5.DISPLAY, colours.rgb(colour_hexa), pygame.Rect(tx, ty, dx, dy), 1
    )


def fillRect(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pygame.draw.rect(M5.DISPLAY, colours.rgb(colour_hexa), pygame.Rect(tx, ty, dx, dy))


def drawCircle(cx: int, cy: int, radius: int, colour_hexa: int):
    pygame.draw.circle(M5.DISPLAY, colours.rgb(colour_hexa), (cx, cy), radius, 1)


def fillCircle(cx: int, cy: int, radius: int, colour_hexa: int):
    pygame.draw.circle(M5.DISPLAY, colours.rgb(colour_hexa), (cx, cy), radius)
