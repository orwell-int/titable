from colours import Colour
import colours
import blocks
from logic import Player
from logic import Strategies
import logic

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


class SillyText:
    def __init__(self):
        self._text = None

    def _set_text(self, text):
        self._text.text = text

    text = property(fset=_set_text)

    del _set_text

    def draw(self):
        self._text.draw()


class TextRound(SillyText):
    def __init__(self, text_colour, fill_colour):
        cx = LEFT_BAR_WIDTH // 2
        cy = MAX_Y // 2 - 20
        self._text = blocks.DecorationText(
            "",
            cx,
            cy,
            text_colour,
            fill_colour,
            font=Widgets.FONTS.DejaVu18,
        )


class TextTurn(SillyText):
    def __init__(self, text_colour, fill_colour):
        cx = LEFT_BAR_WIDTH // 2
        cy = MAX_Y // 2 + 20
        self._text = blocks.DecorationText(
            "",
            cx,
            cy,
            text_colour,
            fill_colour,
            font=Widgets.FONTS.DejaVu18,
        )


class Screen:
    COLOUR_BORDER = colours.PALETTE_GOLD

    def __init__(
        self,
        name,
        title,
        title_colour,
        side_colour=None,
        has_return=True,
        game=None,
        has_round=False,
        has_turn=False,
    ):
        self.name = name
        self.title = title
        if title_colour is not None:
            self.title_colour = title_colour
        else:
            self.title_colour = side_colour.get_contrasting_text()
        if side_colour is None:
            side_colour = colours.PALETTE_DARK_GREEN
        self._side_colour = side_colour
        self.title_rectangle = blocks.Rectangle(
            1,
            1,
            MAX_X - 1,
            TITLE_HEIGHT,
            title,
            side_colour,
            Screen.COLOUR_BORDER,
        )
        self.left_bar = blocks.Rectangle(
            1,
            TITLE_HEIGHT,
            LEFT_BAR_WIDTH,
            MAX_Y - TITLE_HEIGHT,
            None,
            side_colour,
            Screen.COLOUR_BORDER,
        )
        self.line = blocks.Line(
            2,
            TITLE_HEIGHT,
            LEFT_BAR_WIDTH - 1,
            TITLE_HEIGHT,
            side_colour,
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
        if has_round:
            self._text_round = TextRound(
                self.title_colour,
                self._side_colour,
            )
        else:
            self._text_round = None
        if has_turn:
            self._text_turn = TextTurn(
                self.title_colour,
                self._side_colour,
            )
        else:
            self._text_turn = None
        self._game = game

    def update(self):
        if self._text_round:
            self._text_round.text = f"R {self._game.round}"
        if self._text_turn:
            self._text_turn.text = f"T {self._game.turn}"

    def draw(self):
        self.title_rectangle.draw()
        self.left_bar.draw()
        self.line.draw()
        self.background.draw()
        if self.return_button:
            self.return_button.draw()
        if self._text_round:
            self._text_round.draw()
        if self._text_turn:
            self._text_turn.draw()

    def _create_grid_players(self, button_font, players):
        num_columns = 2
        num_lines = 3
        button_sx = (INNER_X + 2) // num_columns
        button_sy = (INNER_Y + 2) // num_lines
        num_players = len(players)
        buttons = []
        rectangles = []
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
                    buttons.append(button)
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
                    rectangles.append(rectangle)
        return (buttons, rectangles)


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
        self._players = players
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
        self._buttons, self._rectangles = self._create_grid_players(
            button_font, players
        )

    def draw(self):
        super().draw()
        self._button_colour_name.draw()
        for button in self._buttons:
            button.draw()
        for rectangle in self._rectangles:
            rectangle.draw()


class LetterLoop:
    def __init__(self, offset: int, start_index: int = 0):
        self._letters = [chr(ord("A") + ((i + offset) % 26)) for i in range(26)]
        self._index = start_index

    def __getitem__(self, index):
        if index in (-1, 0, 1):
            specific_index = self._index + index
            adjusted_index = specific_index % 26
            return self._letters[adjusted_index]
        else:
            raise Exception(f"Only -1, 0 or 1 allowed but index = {index}")

    def increment(self):
        self._index = (self._index + 1) % 26

    def decrement(self):
        self._index = (self._index - 1) % 26


class ScreenSetupName(Screen):
    """
    The custom part should look like this
    <---------- INNER_X ---------->
    +-----+-----+-----+-----+-----+   ^
    |     |     |     |     |     |   |
    |     |  A  |  B  |  C  |     |   |
    |     |     |     |     |     |   |
    +     +     +     +     +     +   |
    |     |     |     |     |     |
    |  <  |  L  |  M  |  N  |  >  | INNER_Y
    |     |     |     |     |     |
    +     +     +     +     +     +   |
    |     |     |     |     |     |   |
    |     |  T  |  U  |  V  |     |   |
    |     |     |     |     |     |   |
    +-----+-----+-----+-----+-----+   v
    Offset for the three lines found using:
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    LMNOPQRSTUVWXYZABCDEFGHIJK
    TUVWXYZABCDEFGHIJKLMNOPQRS
    """

    def __init__(self, players: list[Player], player_index: int):
        player = players[player_index]
        super().__init__("setup colour", player.name, player.colour)
        super().__init__("setup name", players[player_index].name + "_", colours.WHITE)
        button_font = Widgets.FONTS.DejaVu24
        rectangle_font = Widgets.FONTS.DejaVu18
        letters_by_line = [
            LetterLoop(0),
            LetterLoop(11),
            LetterLoop(19),
        ]
        num_columns = 5
        num_lines = 3
        item_sx = (INNER_X + 1) // num_columns + 1
        item_sy = (INNER_Y + 1) // num_lines + 1
        self._button_left = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            item_sx,
            INNER_Y + 1,
            "<<<",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        x = LEFT_BAR_WIDTH + 4 * (item_sx - 1)
        self._button_right = blocks.ButtonRectangle(
            x,
            TITLE_HEIGHT,
            MAX_X - x,
            INNER_Y + 1,
            ">>>",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        self._buttons = []
        self._rectangles = []
        for line in range(num_lines):
            last_line = line == (num_lines - 1)
            letter_line = letters_by_line[line]
            for column in range(1, num_columns - 1):
                letter_index = column - 2
                letter = letter_line[letter_index]
                is_button = column == 2
                x = LEFT_BAR_WIDTH + (item_sx - 1) * column
                y = TITLE_HEIGHT + (item_sy - 1) * line
                sx = item_sx
                sy = MAX_Y - y if (last_line) else item_sy
                if is_button:
                    button = blocks.ButtonRectangle(
                        x,
                        y,
                        sx,
                        sy,
                        letter,
                        colours.PALETTE_LIGHT_GREEN,
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
                        letter,
                        colours.PALETTE_DARK_BLUE,
                        Screen.COLOUR_BORDER,
                        rectangle_font,
                    )
                    self._rectangles.append(rectangle)
        x = LEFT_BAR_WIDTH // 2
        y = MAX_Y - x
        self._button_erase = blocks.ButtonCircle(
            x,
            y,
            x - 4,
            "<|",
            colours.PALETTE_LIGHT_GREEN,
            colours.PALETTE_LIGHT_GREEN,
            # Screen.COLOUR_BORDER,
        )

    def draw(self):
        super().draw()
        self._button_erase.draw()
        self._button_left.draw()
        self._button_right.draw()
        for button in self._buttons:
            button.draw()
        for rectangle in self._rectangles:
            rectangle.draw()


class ScreenSetupColour(Screen):
    def __init__(self, players: list[Player], player_index: int):
        colours_to_players = {}
        for player in players:
            if player.colour != colours.PLAYER_BLANK:
                colours_to_players[player.colour] = player
        can_swap = len(colours_to_players) == len(players)
        player = players[player_index]
        super().__init__(
            "setup colour", player.name, title_colour=None, side_colour=player.colour
        )
        button_font = Widgets.FONTS.DejaVu18
        num_columns = 3
        num_lines = 3
        dx = 4
        dy = 4
        sx = (INNER_X - (1 + num_columns) * dx) // num_columns  # ~ 85
        sy = (INNER_Y - (1 + num_lines) * dy) // num_lines  # ~ 65
        self._buttons = []
        self._center_control = None
        index = 0
        for column in range(num_columns):
            for line in range(num_lines):
                disable = False
                is_colour = not ((line == 1) and (column == 1))
                if is_colour:
                    colour = colours.PLAYER_COLOURS[index]
                    is_button = True
                    if colour in colours_to_players:
                        text = colours_to_players[colour].name
                        disable = not can_swap
                    else:
                        text = colour.pretty_name[len("player ") :]
                        disable = can_swap
                    index += 1
                else:
                    colour = colours.PLAYER_BLANK
                    if can_swap:
                        text = "swap"
                    else:
                        text = "back"
                    is_button = can_swap
                if is_button:
                    control = blocks.ButtonRectangle(
                        LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                        TITLE_HEIGHT + dy + (dy + sy) * line,
                        sx,
                        sy,
                        text,
                        colour,
                        Screen.COLOUR_BORDER,
                    )
                    if disable:
                        control.enabled = False
                else:
                    control = blocks.Rectangle(
                        LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                        TITLE_HEIGHT + dy + (dy + sy) * line,
                        sx,
                        sy,
                        text,
                        colour,
                        Screen.COLOUR_BORDER,
                    )
                if is_colour:
                    self._buttons.append(control)
                else:
                    self._center_control = control

    def draw(self):
        super().draw()
        for button in self._buttons:
            button.draw()
        self._center_control.draw()


class ScreenStrategy(Screen):
    def __init__(self, game: logic.Game):
        super().__init__(
            "strategy", None, colours.WHITE, side_colour=None, game=game, has_round=True
        )
        self._game = game
        self._players = game.players
        button_font = Widgets.FONTS.DejaVu18
        dy = 4
        top_button_sy = TITLE_HEIGHT - dy * 2
        top_button_sx = 180
        delta_x = (MAX_X - LEFT_BAR_WIDTH - top_button_sx) // 2
        self._button_end_phase = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH + delta_x,
            dy,
            top_button_sx,
            top_button_sy,
            "End strategy phase",
            colours.PALETTE_LIGHT_GREEN,
            colours.PALETTE_LIGHT_GREEN,
            # Screen.COLOUR_BORDER,
            button_font,
        )
        self._buttons, self._rectangles = self._create_grid_players(
            button_font, self._players
        )
        self._text_strategies = []
        for button, player in zip(self._buttons, self._players):
            cx, cy = button.center
            text = Strategies.to_short_string(player.strategy)
            text_strategy = blocks.DecorationText(
                text,
                cx,
                cy + 20,
                button.text_colour,
                button.fill_colour,
                font=Widgets.FONTS.DejaVu18,
            )
            self._text_strategies.append(text_strategy)
        self.update()

    def update(self):
        super().update()
        all_selected = all(
            [player.strategy != Strategies.NONE for player in self._players]
        )
        self._button_end_phase.enabled = all_selected

    def draw(self):
        super().draw()
        self._button_end_phase.draw()
        for button in self._buttons:
            button.draw()
        for rectangle in self._rectangles:
            rectangle.draw()
        for text_strategy in self._text_strategies:
            text_strategy.draw()


class ScreenStrategyPlayer(Screen):
    def __init__(self, game: logic.Game, player_num: int):
        strategies_to_players = {}
        can_swap = True
        for player in game.players:
            if player.strategy != Strategies.NONE:
                strategies_to_players[player.strategy] = player
            else:
                can_swap = False
        player = game.get_player(player_num)
        super().__init__(
            "setup colour",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        button_font = Widgets.FONTS.DejaVu18
        num_columns = 3
        num_lines = 3
        dx = 4
        dy = 4
        sx = (INNER_X - (1 + num_columns) * dx) // num_columns  # ~ 85
        sy = (INNER_Y - (1 + num_lines) * dy) // num_lines  # ~ 65
        self._buttons = []
        self._center_control = None
        strategy_index = 1
        for line in range(num_lines):
            for column in range(num_columns):
                disable = False
                is_colour = not ((line == 1) and (column == 1))
                if is_colour:
                    colour = Strategies.to_colour(strategy_index)
                    is_button = True
                    if strategy_index in strategies_to_players:
                        text = strategies_to_players[strategy_index].name
                        disable = not can_swap
                    else:
                        text = f"{strategy_index} [{game.available_strategies[strategy_index]}]"
                        disable = can_swap
                    strategy_index += 1
                else:
                    colour = colours.PLAYER_BLANK
                    if can_swap:
                        text = "swap"
                    else:
                        text = "back"
                    is_button = can_swap
                if is_button:
                    control = blocks.ButtonRectangle(
                        LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                        TITLE_HEIGHT + dy + (dy + sy) * line,
                        sx,
                        sy,
                        text,
                        colour,
                        Screen.COLOUR_BORDER,
                    )
                    if disable:
                        control.enabled = False
                else:
                    control = blocks.Rectangle(
                        LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                        TITLE_HEIGHT + dy + (dy + sy) * line,
                        sx,
                        sy,
                        text,
                        colour,
                        Screen.COLOUR_BORDER,
                    )
                if is_colour:
                    self._buttons.append(control)
                else:
                    self._center_control = control
        self.update()

    def draw(self):
        super().draw()
        for button in self._buttons:
            button.draw()
        self._center_control.draw()


class ScreenAction(Screen):
    """
    The custom part should look like this
    <---------- INNER_X ---------->
    +-------+---+-----+---+-------+   ^
    |       |             |       |   |
    |       |  Strategy   |       |   |
    |       |    (x)      |       |   |
    +       +---+-----+---+       +   |
    |Previou|  Tactical   | Next  |
    |       |     /       |       | INNER_Y
    |player |  Component  |player |
    +       +---+-----+---+       +   |
    |       |             |       |   |
    |       |    Pass     |       |   |
    |       |             |       |   |
    +-------+---+-----+---+-------+   v
      2.5         3.0        2.5
    Maybe a bit of spacing between the buttons if possible.
    """

    def __init__(self, game: logic.Game):
        # game.current_player seems better then game.get_player(index)
        player = game.current_player
        super().__init__(
            "action",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        button_font = Widgets.FONTS.DejaVu18
        x_weight_player_button = 2.5
        x_weight_action_button = 3
        x_ratio_player_button = x_weight_player_button / (
            x_weight_player_button * 2 + x_weight_action_button
        )
        player_button_sx = int(x_ratio_player_button * (INNER_X + 1))
        action_button_sx = (INNER_X + 1) - 2 * player_button_sx

        text_previous = "previous"
        self._button_previous = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_previous,
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )

        text_next = "next"
        self._button_next = blocks.ButtonRectangle(
            MAX_X - player_button_sx,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_next,
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        self.update()

    def draw(self):
        super().draw()
        self._button_previous.draw()
        self._button_next.draw()


def main():
    import sys
    import M5
    import logic

    M5.begin()
    select = 1
    if len(sys.argv) > 1:
        try:
            param = int(sys.argv[1])
            if 0 < param <= 14:
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
    elif 4 == select:
        game = logic.Game.build_fake_game()
        screen_setup_name = ScreenSetupName(game.players, 2)
        screen_setup_name.draw()
    elif 5 == select:
        game = logic.Game()
        screen_setup_name = ScreenSetupName(game.players, 2)
        screen_setup_name.draw()
    elif 6 == select:
        game = logic.Game.build_fake_game()
        screen_setup_colour = ScreenSetupColour(game.players, 4)
        screen_setup_colour.draw()
    elif 7 == select:
        game = logic.Game()
        screen_setup_colour = ScreenSetupColour(game.players, 4)
        screen_setup_colour.draw()
    elif 8 == select:
        game = logic.Game()
        player = game.get_player(2)
        player.name = "Pierre"
        player.colour = colours.PLAYER_BLACK
        screen_setup_colour = ScreenSetupColour(game.players, 4)
        screen_setup_colour.draw()
    elif 9 == select:
        game = logic.Game.build_fake_game()
        screen_setup_colour = ScreenStrategy(game)
        screen_setup_colour.draw()
    elif 10 == select:
        game = logic.Game.build_fake_game()
        game.start_playing()
        player = game.get_next_player()
        player.strategy = Strategies.WARFARE
        player = game.get_next_player()
        player.strategy = Strategies.TECHNOLOGY
        screen_setup_colour = ScreenStrategy(game)
        screen_setup_colour.draw()
    elif 11 == select:
        game = logic.Game.build_fake_game()
        game.start_playing()
        screen_setup_colour = ScreenStrategyPlayer(game, player_num=5)
        screen_setup_colour.draw()
    elif 12 == select:
        game = logic.Game.build_fake_game()
        game.start_playing()
        player = game.get_next_player()
        player.strategy = Strategies.WARFARE
        player = game.get_next_player()
        player.strategy = Strategies.TECHNOLOGY
        screen_setup_colour = ScreenStrategyPlayer(game, player_num=5)
        screen_setup_colour.draw()
    elif select in (
        13,
        14,
    ):
        game = logic.Game.build_fake_game()
        game.start_playing()
        player = game.get_next_player()
        player.strategy = Strategies.WARFARE
        player = game.get_next_player()
        player.strategy = Strategies.TECHNOLOGY
        player = game.get_next_player()
        player.strategy = Strategies.DIPLOMACY
        player = game.get_next_player()
        player.strategy = Strategies.CONSTRUCTION
        player = game.get_next_player()
        player.strategy = Strategies.TRADE
        player = game.get_next_player()
        player.strategy = Strategies.LEADERSHIP
        if 13 == select:
            screen_setup_colour = ScreenStrategyPlayer(game, player.num)
            screen_setup_colour.draw()
        elif 14 == select:
            screen_setup_colour = ScreenAction(game)
            screen_setup_colour.draw()
    M5.update()


if "__main__" == __name__:
    main()
