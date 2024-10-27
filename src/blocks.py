from colours import Colour


class Decoration:
    pass


class ButtonRectangle:
    def __init__(
        self,
        x: int,
        y: int,
        decoration,
        align_decoration_h: HorizontalAlignment,
        align_decoration_v: VerticalAlignment,
        fill_colour: Colour,
        border_colour: Colour,
        disabled_fill_colour: Colour = None,
        disabled_border_colour: Colour = None,
    ):
        self.x = x
        self.y = y
        self.decoration = decoration
        self.align_decoration_h = align_decoration_h
        self.align_decoration_v = align_decoration_v
        self.fill_colour = fill_colour
        self.border_colour = border_colour
        if disabled_fill_colour is None:
            self.disabled_fill_colour = fill_colour.build_different()
        else:
            self.disabled_fill_colour = disabled_fill_colour
        if disabled_border_colour is None:
            self.disabled_border_colour = border_colour.build_different()
        else:
            self.disabled_border_colour = disabled_border_colour
