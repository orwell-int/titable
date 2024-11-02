from . import Widgets

FONT = 0


def setFont(index: int):
    global FONT
    FONT = index


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
    pass


def drawString(text: str, tx: int, ty: int):
    pass


def drawRect(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pass


def fillRect(tx: int, ty: int, dx: int, dy: int, colour_hexa: int):
    pass
