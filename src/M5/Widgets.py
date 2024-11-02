class FONTS:
    DejaVu18 = 3
    DejaVu12 = 2


class Rectangle:
    def __init__(self, x, y, dx, dy, border_colour, fill_colour):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.border_colour = border_colour
        self.fill_colour = fill_colour
        self.visible = True

    def setCursor(self, x, y):
        self.x = x
        self.y = y

    def setSize(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def setColor(self, border_colour, fill_colour):
        self.border_colour = border_colour
        self.fill_colour = fill_colour

    def setVisible(self, value):
        self.visible = value


class Circle:
    def __init__(self, x, y, radius, border_colour, fill_colour):
        self.x = x
        self.y = y
        self.radius = radius
        self.border_colour = border_colour
        self.fill_colour = fill_colour
        self.visible = True

    def setCursor(self, x, y):
        self.x = x
        self.y = y

    def setRadius(self, radius):
        self.radius = radius

    def setColor(self, border_colour, fill_colour):
        self.border_colour = border_colour
        self.fill_colour = fill_colour

    def setVisible(self, value):
        self.visible = value


class Title:
    def __init__(self, text, x_text, text_colour, fill_colour, font=FONTS.DejaVu18):
        self.text = text
        self.x_text = x_text
        self.text_colour = text_colour
        self.fill_colour = fill_colour
        self.font = font
        self.visible = True

    def setText(self, text):
        self.text = text

    def setTextCursor(self, x_text):
        self.x_text = x_text

    def setColor(self, text_colour, fill_colour):
        self.text_colour = text_colour
        self.fill_colour = fill_colour

    def setVisible(self, value):
        self.visible = value


class Line:
    def __init__(self, x1, y1, x2, y2, colour):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colour = colour
        self.visible = True

    def setPoints(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def setColor(self, colour):
        self.colour = colour


class Triangle:
    def __init__(self, x1, y1, x2, y2, x3, y3, border_colour, fill_colour):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.border_colour = border_colour
        self.fill_colour = fill_colour
        self.visible = True

    def setPoints(self, x1, y1, x2, y2, x3, y3):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

    def setColor(self, border_colour, fill_colour):
        self.border_colour = border_colour
        self.fill_colour = fill_colour

    def setVisible(self, value):
        self.visible = value


class Label:
    def __init__(
        self,
        text,
        x,
        y,
        size,
        text_colour,
        backgroud_colour,
        font,  # =FONTS.DejaVu18
    ):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.text_colour = text_colour
        self.backgroud_colour = backgroud_colour
        self.font = font

    def setText(self, text):
        self.text = text

    def setCursor(self, x, y):
        self.x = x
        self.y = y

    def setColor(self, text_colour, backgroud_colour):
        self.text_colour = text_colour
        self.backgroud_colour = backgroud_colour

    def setSize(self, size):
        self.size

    def setFont(self, font):
        self.font = font

    def setVisible(self, value):
        self.visible = value
