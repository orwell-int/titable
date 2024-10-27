class Colour:
    def __init__(self, r: int, g: int, b: int):
        if not 0 <= r <= 255:
            raise Exception(f"Invalid r: ! 0 <= {r} <= 255")
        if not 0 <= g <= 255:
            raise Exception(f"Invalid g: ! 0 <= {g} <= 255")
        if not 0 <= b <= 255:
            raise Exception(f"Invalid b: ! 0 <= {b} <= 255")
        self.r = r
        self.g = g
        self.b = b
        self._pretty_name = None

    def _build_different(self, v):
        if v < 128:
            delta = 255 - v
            v = 255 - delta // 2
        else:
            delta = v - 0
            v = 0 + delta // 2
        return v

    def build_different(self):
        return Colour(
            self._build_different(self.r),
            self._build_different(self.g),
            self._build_different(self.b),
        )

    def _linearize(self, v):
        if v <= 0.04045:
            return v / 12.92
        else:
            return pow(((v + 0.055) / 1.055), 2.4)

    def percieved_lightness(self):
        r_lin = self._linearize(self.r)
        g_lin = self._linearize(self.g)
        b_lin = self._linearize(self.b)
        luminance = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        if luminance <= 0.008856:
            percieved_lightness = luminance * 903.3
        else:
            percieved_lightness = pow(luminance, 1 / 3) * 116 - 16
        return percieved_lightness

    @property
    def hexa(self):
        return hex((self.r << 16) + (self.g << 8) + self.b)

    @property
    def pretty_name(self):
        return self._pretty_name

    @pretty_name.setter
    def pretty_name(self, pretty_name):
        self._pretty_name = pretty_name

    def __repr__(self):
        return f"Colour(r={self.r}, g={self.g}, b={self.b})"

    def __str__(self):
        if self._pretty_name:
            return self._pretty_name
        else:
            return self.__repr__()

    def __hash__(self):
        return (self.r << 16) + (self.g << 8) + self.b


# colour for player that had not picked a colour yet
BLANK = Colour(255, 255, 255)

BLACK = Colour(2, 2, 2)
BLACK.pretty_name = "black"
BLUE = Colour(26, 57, 147)
BLUE.pretty_name = "blue"
GREEN = Colour(11, 93, 34)
GREEN.pretty_name = "green"
ORANGE = Colour(234, 86, 6)
ORANGE.pretty_name = "orange"
PINK = Colour(204, 74, 173)
PINK.pretty_name = "pink"
PURPLE = Colour(96, 19, 88)
PURPLE.pretty_name = "purple"
RED = Colour(169, 34, 34)
RED.pretty_name = "red"
YELLOW = Colour(254, 230, 25)
YELLOW.pretty_name = "yellow"
