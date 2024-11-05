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

    @staticmethod
    def from_hexa_str(hexa: str):
        length = len(hexa)
        if 5 == length:
            hexa = "0" + hexa
        r = int(hexa[0:2], 16)
        g = int(hexa[2:4], 16)
        b = int(hexa[4:6], 16)
        return Colour(r, g, b)

    def _build_different(self, v, perceived_lightness, factor=0.5):
        if not (0.0 < factor < 1.0):
            raise Exception(
                f"_build_different: factor must be in ]0.0 .. 1.0[ but is {factor}"
            )
        if perceived_lightness < 50:
            delta = 255 - v
            v = 255 - int(delta * factor)
        else:
            delta = v - 0
            v = 0 + int(delta * factor)
        return v

    def build_different(self, factor=0.5):
        perceived_lightness = self.get_perceived_lightness()
        return Colour(
            self._build_different(self.r, perceived_lightness, factor),
            self._build_different(self.g, perceived_lightness, factor),
            self._build_different(self.b, perceived_lightness, factor),
        )

    def _linearize(self, v):
        v = v / 255
        if v <= 0.04045:
            return v / 12.92
        else:
            return pow(((v + 0.055) / 1.055), 2.4)

    def get_perceived_lightness(self):
        r_lin = self._linearize(self.r)
        g_lin = self._linearize(self.g)
        b_lin = self._linearize(self.b)
        luminance = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        if luminance <= 0.008856:
            perceived_lightness = luminance * 903.3
        else:
            perceived_lightness = pow(luminance, 1 / 3) * 116 - 16
        return perceived_lightness

    def get_contrasting_text(self):
        if self.get_perceived_lightness() < 50:
            return WHITE
        else:
            return BLACK

    @property
    def hexa(self):
        return (self.r << 16) + (self.g << 8) + self.b

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


def rgb(hexa_value: int):
    r = hexa_value >> 16
    hexa_value -= r << 16
    g = hexa_value >> 8
    b = hexa_value - (g << 8)
    result = (r, g, b)
    return result


WHITE = Colour(255, 255, 255)
WHITE.pretty_name = "white"
BLACK = Colour(0, 0, 0)
BLACK.pretty_name = "black"

# colour for a player that had not picked a colour yet
PLAYER_BLANK = Colour(255, 255, 255)
PLAYER_BLANK.pretty_name = "player blank"

PLAYER_BLACK = Colour(2, 2, 2)
PLAYER_BLACK.pretty_name = "player black"
PLAYER_BLUE = Colour(26, 57, 147)
PLAYER_BLUE.pretty_name = "player blue"
PLAYER_GREEN = Colour(11, 93, 34)
PLAYER_GREEN.pretty_name = "player green"
PLAYER_ORANGE = Colour(234, 86, 6)
PLAYER_ORANGE.pretty_name = "player orange"
PLAYER_PINK = Colour(234, 60, 230)
PLAYER_PINK.pretty_name = "player pink"
PLAYER_PURPLE = Colour(96, 19, 88)
PLAYER_PURPLE.pretty_name = "player purple"
PLAYER_RED = Colour(169, 34, 34)
PLAYER_RED.pretty_name = "player red"
PLAYER_YELLOW = Colour(254, 230, 25)
PLAYER_YELLOW.pretty_name = "player yellow"

PLAYER_COLOURS = [
    PLAYER_BLACK,
    PLAYER_BLUE,
    PLAYER_GREEN,
    PLAYER_ORANGE,
    PLAYER_PINK,
    PLAYER_PURPLE,
    PLAYER_RED,
    PLAYER_YELLOW,
]

PALETTE_DARK_BLUE = Colour.from_hexa_str("192B48")
PALETTE_DARK_BLUE.pretty_name = "oxford blue"
PALETTE_DARK_GREEN = Colour.from_hexa_str("212B1E")
PALETTE_DARK_GREEN.pretty_name = "black olive"
PALETTE_LIGHT_BLUE = Colour.from_hexa_str("1379BD")
PALETTE_LIGHT_BLUE.pretty_name = "honolulu blue"
PALETTE_LIGHT_GREEN = Colour.from_hexa_str("517A33")
PALETTE_LIGHT_GREEN.pretty_name = "fern green"
PALETTE_GOLD = Colour.from_hexa_str("BA862B")
PALETTE_GOLD.pretty_name = "dark goldenrod"
