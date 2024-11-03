from colours import Colour
import colours
import blocks


# there is always a title with a "back" button
class ScreenTypes:
    # a few buttons spread vertically
    WELCOME = 0
    # players 2 x 3 with switch between name and colour
    CONFIG_PLAYERS = 1
    # fancy letters selector with erase button
    CONFIG_PLAYER_NAME = 2
    # 3 x 3 buttons (colour -> name + disabled as colours get picked)
    CONFIG_PLAYER_COLOUR = 3
    # players 2 x 3 (with selected strategy) with button to end strategy phase
    # (button only enabled when every player has picked)
    # shows round (and turn) in left bar
    STRATEGY_MAIN = 4
    # player dedicated 3 x 3 buttons (number [trade goods] -> name)
    # add swap option in the middle when every player has picked something
    # shows round (and turn) in left bar
    STRATEGY_PLAYER = 5
    # player dedicated three vertical buttons to chose type of action + one for next (player / phase)
    # should it include one button to go back to previous?
    # shows round and turn in left bar
    ACTION_PLAYER = 6
    # player dedicated one button for previous + text + one for next (player / round)
    STATUS_PLAYER = 7


MAX_X = 320
MAX_Y = 240
TITLE_HEIGHT = 24
LEFT_BAR_WIDTH = 50


class Screen:
    def __init__(
        self,
        name,
        title,
        title_colour,
    ):
        self.name = name
        self.title = title
        self.x_text = 80
        self.title_colour = title_colour
        self.title_rectangle = blocks.Rectangle(
            1, 1, MAX_X, TITLE_HEIGHT, title, Colour(200, 200, 250)
        )
        self.left_bar = blocks.Rectangle(
            1, TITLE_HEIGHT + 1, LEFT_BAR_WIDTH, MAX_Y, None, Colour(200, 250, 200)
        )

    def draw(self):
        self.title_rectangle.draw()
        self.left_bar.draw()


class ScreenWelcome(Screen):
    def __init__(self):
        super().__init__("welcome", "TI 4 assistant", colours.WHITE)
        button_x_offset = 110
        button_sx = 150
        button_sy = 65
        dx = 4
        dy = 4
        self._button_setup = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy,
            button_sx,
            button_sy,
            "Setup",
            Colour(120, 120, 120),
        )
        play_or_resume = "Play"
        self._button_play = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy + button_sy + dy,
            button_sx,
            button_sy,
            play_or_resume,
            Colour(120, 120, 120),
        )
        self._button_reset = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy + (button_sy + dy) * 2,
            button_sx,
            button_sy,
            "Reset",
            Colour(120, 120, 120),
        )

    def draw(self):
        super().draw()
        self._button_setup.draw()
        self._button_play.draw()
        self._button_reset.draw()


def main():
    import M5

    M5.begin()
    screen_welcome = ScreenWelcome()
    screen_welcome.draw()
    M5.update()


if "__main__" == __name__:
    main()
