from . import Widgets

FONT = 0


def setFont(index: int):
    global FONT
    FONT = index


def textWodth(text: str) -> int:
    return 0


def getFontHeight() -> int:
    global FONT
    if Widgets.FONT.DejaVu18 == FONT:
        return 18
    else:
        # not implemented
        return 0


def setTextColor(text_colour_hexa: int, fill_colour_hexa: int):
    pass


def drawString(text: str, tx: int, ty: int):
    pass


def drawRectangle(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pass


def fillRectangle(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pass
