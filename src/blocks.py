from colours import Colour
import colours

import M5
from M5 import Lcd
from M5 import Widgets


class Decoration:
    def has_colours(self):
        return False


class DecorationText(Decoration):
    def __init__(
        self,
        text,
        cx,
        cy,
        text_colour: Colour,
        fill_colour: Colour,
        font=Widgets.FONTS.DejaVu12,
    ):
        super().__init__()
        self._text = text
        self._cx = cx
        self._cy = cy
        self._text_colour = text_colour
        self._fill_colour = fill_colour
        self._font = font
        self._visible = True
        self._changed = True

    def hide(self):
        if self._visible:
            self._visible = False
            self._changed = True

    def show(self):
        if not self._visible:
            self._visible = True
            self._changed = True

    def draw(self):
        if self._changed:
            Lcd.setFont(self._font)
            width = Lcd.textWidth(self._text)
            height = Lcd.fontHeight()
            tx = self._cx - width // 2
            ty = self._cy - height // 2
            if self._visible:
                Lcd.setTextColor(self._text_colour.hexa, self._fill_colour.hexa)
                Lcd.drawString(self._text, tx, ty)
            else:
                Lcd.fillRect(tx, ty, width, height, colours.BLACK)
            self._changed = False

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        if self._text != text:
            self._text = text
            self._changed = True

    @property
    def text_colour(self):
        return self._text_colour

    @text_colour.setter
    def text_colour(self, text_colour: Colour):
        if self._text_colour != text_colour:
            self._text_colour = text_colour
            self._changed = True

    @property
    def fill_colour(self):
        return self._fill_colour

    @fill_colour.setter
    def fill_colour(self, fill_colour: Colour):
        if self._fill_colour != fill_colour:
            self._fill_colour = fill_colour
            self._changed = True

    def has_colours(self):
        return True


class DecorationImage(Decoration):
    def __init__(self, path, x, y):
        super().__init__()
        self._path = path
        self._x = x
        self._y = y
        self.image = Widgets.Image(path, x, y)


class AlignmentHorizontal:
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class AlignmentVertical:
    TOP = 0
    CENTER = 1
    BOTTOM = 2


class Rectangle:
    def __init__(
        self,
        x: int,
        y: int,
        dx: int,
        dy: int,
        # decoration,  # text or image
        text: str,
        # align_decoration_h: int,
        # align_decoration_v: int,
        fill_colour: Colour,
        border_colour: Colour = colours.WHITE,
    ):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        # self.decoration = decoration
        self._text = text
        # self.align_decoration_h = align_decoration_h
        # self.align_decoration_v = align_decoration_v
        self._fill_colour = fill_colour
        self._border_colour = border_colour
        self._text_colour = self._fill_colour.get_contrasting_text()
        if text:
            self.decoration_text = DecorationText(
                self._text,
                x + dx // 2,
                y + dy // 2,
                self._text_colour,
                self._fill_colour,
            )
        else:
            self.decoration_text = None
        self._changed = True

    @property
    def text(self):
        return self._text

    @property
    def text_colour(self):
        return self._text_colour

    @text_colour.setter
    def text_colour(self, text_colour: Colour):
        self._text_colour = text_colour
        self._changed = True

    @property
    def fill_colour(self):
        return self._fill_colour

    @fill_colour.setter
    def fill_colour(self, fill_colour: Colour):
        self._fill_colour = fill_colour
        # use setter on purpose
        self.text_colour = self._fill_colour.get_contrasting_text()
        self._changed = True

    @property
    def border_colour(self):
        return self._border_colour

    @border_colour.setter
    def border_colour(self, border_colour: Colour):
        self._border_colour = border_colour
        self._changed = True

    def __repr__(self):
        string = f"ButtonRectangle(x={self.x}, y={self.y}, "
        # string += f"decoration={self.decoration}, "
        string += f"text={self._text}, "
        # string += f"align_decoration_h={self.align_decoration_h}, "
        # string += f"align_decoration_v={self.align_decoration_v}, "
        string += f"fill_colour={self._fill_colour}, "
        string += f"border_colour={self._border_colour}, "
        string += f"text_colour={self._text_colour}, "
        string += f"changed={self._changed})"
        return string

    def __str__(self):
        return self.__repr__()

    def draw(self):
        if self._changed:
            Lcd.drawRect(self.x, self.y, self.dx, self.dy, self._border_colour.hexa)
            Lcd.fillRect(
                self.x + 1,
                self.y + 1,
                self.dx - 2,
                self.dy - 2,
                self._fill_colour.hexa,
            )
            if self.decoration_text:
                self.decoration_text.draw()


class ButtonRectangle:
    def __init__(
        self,
        x: int,
        y: int,
        dx: int,
        dy: int,
        # decoration,  # text or image
        text: str,
        # align_decoration_h: int,
        # align_decoration_v: int,
        fill_colour: Colour,
        border_colour: Colour = colours.WHITE,
        disabled_fill_colour: Colour = None,
        disabled_border_colour: Colour = None,
    ):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        # self.decoration = decoration
        self._text = text
        # self.align_decoration_h = align_decoration_h
        # self.align_decoration_v = align_decoration_v
        self._fill_colour = fill_colour
        self._border_colour = border_colour
        self._disabled_fill_colour = disabled_fill_colour
        self._disabled_border_colour = disabled_border_colour
        self._text_colour = self._fill_colour.get_contrasting_text()
        self._disabled_text_colour = self._text_colour.build_different()
        self._current_fill_colour = self._fill_colour
        self._current_border_colour = self._border_colour
        self.decoration_text = DecorationText(
            self._text, x + dx // 2, y + dy // 2, self._text_colour, self._fill_colour
        )
        self._enabled = True
        self._changed = True

    @property
    def text(self):
        return self._text

    @property
    def text_colour(self):
        return self._text_colour

    @text_colour.setter
    def text_colour(self, text_colour: Colour):
        self._text_colour = text_colour
        self._disabled_text_colour = self._text_colour.build_different()
        self._changed = True

    @property
    def fill_colour(self):
        return self._fill_colour

    @fill_colour.setter
    def fill_colour(self, fill_colour: Colour):
        self._fill_colour = fill_colour
        # use setter on purpose
        self.text_colour = self._fill_colour.get_contrasting_text()
        self._changed = True

    @property
    def border_colour(self):
        return self._border_colour

    @border_colour.setter
    def border_colour(self, border_colour: Colour):
        self._border_colour = border_colour
        self._changed = True

    def __repr__(self):
        string = f"ButtonRectangle(x={self.x}, y={self.y}, "
        # string += f"decoration={self.decoration}, "
        string += f"text={self._text}, "
        # string += f"align_decoration_h={self.align_decoration_h}, "
        # string += f"align_decoration_v={self.align_decoration_v}, "
        string += f"fill_colour={self._fill_colour}, "
        string += f"border_colour={self._border_colour}, "
        string += f"disabled_fill_colour={self._disabled_fill_colour}, "
        string += f"disabled_border_colour={self._disabled_border_colour},"
        string += f"text_colour={self._text_colour}, "
        string += f"disabled_text_colour={self._disabled_text_colour}, "
        string += f"enabled={self._enabled}, "
        string += f"changed={self._changed})"
        return string

    def __str__(self):
        return self.__repr__()

    def contains(self, x, y):
        if not self._enabled:
            return False
        return self.x <= x <= (self.x + self.dx) and self.y <= y <= (self.y + self.dy)

    @property
    def enabled(self):
        return self._enabled

    @border_colour.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            if self._enabled:
                self._current_fill_colour = self._fill_colour
                self._current_border_colour = self._border_colour
                self.decoration_text.text_colour = self._text_colour
                self.decoration_text.fill_colour = self._fill_colour
            else:
                if self._disabled_fill_colour is None:
                    disabled_fill_colour = self._fill_colour.build_different()
                else:
                    disabled_fill_colour = self._disabled_fill_colour
                if self._disabled_border_colour is None:
                    disabled_border_colour = self._border_colour.build_different()
                else:
                    disabled_border_colour = self._disabled_border_colour
                self._current_fill_colour = disabled_fill_colour
                self._current_border_colour = disabled_border_colour
                self.decoration_text.text_colour = self._disabled_text_colour
                self.decoration_text.fill_colour = disabled_fill_colour
            self.enabled = value

    def draw(self):
        if self._changed:
            Lcd.drawRect(
                self.x, self.y, self.dx, self.dy, self._current_border_colour.hexa
            )
            Lcd.fillRect(
                self.x + 1,
                self.y + 1,
                self.dx - 2,
                self.dy - 2,
                self._current_fill_colour.hexa,
            )
            self.decoration_text.draw()


def main():
    M5.begin()
    dx = 4
    dy = 4
    width = 85
    height = 65
    colours.PLAYER_PINK = colours.Colour(234, 60, 230)
    colours_table = [
        colours.PLAYER_BLACK,
        colours.PLAYER_BLUE,
        colours.PLAYER_GREEN,
        colours.PLAYER_ORANGE,
        colours.PLAYER_BLANK,
        colours.PLAYER_PINK,
        colours.PLAYER_PURPLE,
        colours.PLAYER_RED,
        colours.PLAYER_YELLOW,
    ]
    players_table = [
        "ROMAIN",
        "SHIZU",
        "JULIE",
        "PIERRE",
        "SEBASTIEN",
        "FLORENT",
        "MICHAEL",
        "DAMIEN",
        "MASSIMO",
    ]
    for x in range(3):
        for y in range(3):
            current_colour = colours_table[x + 3 * y]
            current_player = players_table[x + 3 * y]
            lightness = current_colour.get_perceived_lightness()
            button = ButtonRectangle(
                dx + (dx + width) * x,
                dy + (dy + height) * y,
                width,
                height,
                f"{current_player}",
                current_colour,
            )
            button.draw()
            print(button)

    M5.update()


if "__main__" == __name__:
    main()
