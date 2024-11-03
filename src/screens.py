from colours import Colour
import colours
import blocks
from logic import Player

from M5 import Widgets


# there is always a title with a "back" button
class ScreenTypes:
    # a few buttons spread vertically
    WELCOME = 0
    # players 2 x 3 with switch between name and colour
    SETUP_PLAYERS = 1
    # fancy letters selector with erase button
    SETUP_PLAYER_NAME = 2
    # 3 x 3 buttons (colour -> name + disabled as colours get picked)
    SETUP_PLAYER_COLOUR = 3
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
TITLE_HEIGHT = 28
LEFT_BAR_WIDTH = 50

INNER_X = MAX_X - LEFT_BAR_WIDTH - 1
INNER_Y = MAX_Y - TITLE_HEIGHT - 1


class Screen:
    COLOUR_BORDER = colours.PALETTE_GOLD

    def __init__(
        self,
        name,
        title,
        title_colour,
        has_return=True,
    ):
        self.name = name
        self.title = title
        self.title_colour = title_colour
        self.title_rectangle = blocks.Rectangle(
            1,
            1,
            MAX_X - 1,
            TITLE_HEIGHT,
            title,
            colours.PALETTE_DARK_GREEN,
            Screen.COLOUR_BORDER,
        )
        self.left_bar = blocks.Rectangle(
            1,
            TITLE_HEIGHT,
            LEFT_BAR_WIDTH,
            MAX_Y - TITLE_HEIGHT,
            None,
            colours.PALETTE_DARK_GREEN,
            Screen.COLOUR_BORDER,
        )
        self.line = blocks.Line(
            2,
            TITLE_HEIGHT,
            LEFT_BAR_WIDTH - 1,
            TITLE_HEIGHT,
            colours.PALETTE_DARK_GREEN,
        )
        self.background = blocks.Rectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            MAX_X - LEFT_BAR_WIDTH,
            MAX_Y - TITLE_HEIGHT,
            None,
            colours.PALETTE_DARK_BLUE,
            Screen.COLOUR_BORDER,
        )
        if has_return:
            max_d = max(LEFT_BAR_WIDTH // 2, TITLE_HEIGHT // 2)
            self.return_button = blocks.ButtonCircle(
                max_d,
                max_d,
                max_d - 4,
                "<<",
                colours.PALETTE_LIGHT_GREEN,
                colours.PALETTE_LIGHT_GREEN,
                # Screen.COLOUR_BORDER,
            )
        else:
            self.return_button = None

    def draw(self):
        self.title_rectangle.draw()
        self.left_bar.draw()
        self.line.draw()
        self.background.draw()
        if self.return_button:
            self.return_button.draw()


class ScreenWelcome(Screen):
    def __init__(self):
        super().__init__("welcome", "TI 4 assistant", colours.WHITE, has_return=False)
        button_sx = 150
        button_sy = 65
        button_x_delta = (MAX_X - (LEFT_BAR_WIDTH + 1) - button_sx) // 2
        button_x_offset = LEFT_BAR_WIDTH + 1 + button_x_delta
        dx = 4
        dy = 4
        button_font = Widgets.FONTS.DejaVu18
        self._button_setup = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy,
            button_sx,
            button_sy,
            "Setup",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        play_or_resume = "Play"
        self._button_play = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy + button_sy + dy,
            button_sx,
            button_sy,
            play_or_resume,
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        self._button_reset = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy + (button_sy + dy) * 2,
            button_sx,
            button_sy,
            "Reset",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )

    def draw(self):
        super().draw()
        self._button_setup.draw()
        self._button_play.draw()
        self._button_reset.draw()


class ScreenSetup(Screen):
    def __init__(self, players: list[Player]):
        super().__init__("setup", None, colours.WHITE)
        button_font = Widgets.FONTS.DejaVu18
        dy = 4
        top_button_sy = TITLE_HEIGHT - dy * 2
        top_button_sx = 100
        delta_x = (MAX_X - LEFT_BAR_WIDTH - top_button_sx) // 2
        self._button_colour_name = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH + delta_x,
            dy,
            top_button_sx,
            top_button_sy,
            "Colour",
            colours.PALETTE_LIGHT_GREEN,
            colours.PALETTE_LIGHT_GREEN,
            # Screen.COLOUR_BORDER,
            button_font,
        )
        num_columns = 2
        num_lines = 3
        button_sx = (INNER_X + 2) // num_columns
        button_sy = (INNER_Y + 2) // num_lines
        num_players = len(players)
        self._buttons = []
        self._rectangles = []
        for line in range(num_lines):
            last_line = line == (num_lines - 1)
            for column in range(num_columns):
                last_column = column == (num_columns - 1)
                index = column + line * num_columns
                x = LEFT_BAR_WIDTH + (button_sx - 1) * column
                y = TITLE_HEIGHT + (button_sy - 1) * line
                sx = MAX_X - x if (last_column) else button_sx
                sy = MAX_Y - y if (last_line) else button_sy
                if index < num_players:
                    player = players[index]
                    button = blocks.ButtonRectangle(
                        x,
                        y,
                        sx,
                        sy,
                        f"{player.name}",
                        player.colour,
                        Screen.COLOUR_BORDER,
                        button_font,
                    )
                    self._buttons.append(button)
                else:
                    rectangle = blocks.Rectangle(
                        x,
                        y,
                        sx,
                        sy,
                        None,
                        colours.WHITE,
                        Screen.COLOUR_BORDER,
                    )
                    self._rectangles.append(rectangle)

    def draw(self):
        super().draw()
        self._button_colour_name.draw()
        for button in self._buttons:
            button.draw()
        for rectangle in self._rectangles:
            rectangle.draw()


def main():
    import sys
    import M5
    import logic

    M5.begin()
    select = 1
    if len(sys.argv) > 1:
        try:
            param = int(sys.argv[1])
            if 0 < param <= 3:
                select = param
        except:
            pass
    if 1 == select:
        screen_welcome = ScreenWelcome()
        screen_welcome.draw()
    elif 2 == select:
        game = logic.Game.build_fake_game()
        screen_setup = ScreenSetup(game.players)
        screen_setup.draw()
    elif 3 == select:
        game = logic.Game()
        screen_setup = ScreenSetup(game.players)
        screen_setup.draw()
    M5.update()


if "__main__" == __name__:
    main()
