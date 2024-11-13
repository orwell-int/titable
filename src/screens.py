from colours import Colour
import colours
import blocks
from logic import Player
from logic import Strategies
import logic
import device
import leds
import events

from M5 import Widgets


ONLY_PRINT = True


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
    # Menu
    MENU = 8
    # Screen opened before the menu
    SAVED_SCREEN = 9


MAX_X = 320
MAX_Y = 240
TITLE_HEIGHT = 28
LEFT_BAR_WIDTH = 50

INNER_X = MAX_X - LEFT_BAR_WIDTH - 1
INNER_Y = MAX_Y - TITLE_HEIGHT - 1


class SillyText:
    def __init__(self, text):
        self._text = text

    @property
    def text(self):
        return self._text.text

    @text.setter
    def text(self, text):
        self._text.text = text

    def draw(self):
        self._text.draw()


class TextRound(SillyText):
    def __init__(self, text_colour, fill_colour):
        cx = LEFT_BAR_WIDTH // 2
        cy = MAX_Y // 2 - 20
        super().__init__(
            blocks.DecorationText(
                "",
                cx,
                cy,
                text_colour,
                fill_colour,
                font=Widgets.FONTS.DejaVu18,
            )
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
        lights: leds.Lights,
        name,
        title,
        title_colour,
        side_colour=None,
        has_return=True,
        game=None,
        has_round=False,
        has_turn=False,
    ):
        global ONLY_PRINT
        self._lights = lights
        self.name = name
        self.title = title
        if title_colour is not None:
            self.title_colour = title_colour
        else:
            self.title_colour = side_colour.get_contrasting_text()
        if side_colour is None:
            side_colour = colours.PALETTE_DARK_GREEN
        self._side_colour = side_colour
        self._game = game
        self._hidden = True
        self._on_return = None
        self._touchables = []
        self.title_rectangle = blocks.Rectangle(
            1,
            1,
            MAX_X - 1,
            TITLE_HEIGHT,
            "",
            side_colour,
            Screen.COLOUR_BORDER,
        )
        cx = (MAX_X - LEFT_BAR_WIDTH) // 2 + LEFT_BAR_WIDTH
        cy = TITLE_HEIGHT // 2
        if title:
            self._title_text = blocks.DecorationText(
                title,
                cx,
                cy,
                side_colour.get_contrasting_text(),
                side_colour,
                font=Widgets.FONTS.DejaVu12,
            )
        else:
            self._title_text = None
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
            self._button_return = blocks.ButtonCircle(
                max_d,
                max_d,
                max_d - 4,
                "<<",
                colours.PALETTE_LIGHT_GREEN,
                colours.PALETTE_LIGHT_GREEN,
                # Screen.COLOUR_BORDER,
            )
            self._button_return.action = lambda args: events.HANDLER.send_event(
                events.RETURN, args
            )
            self._touchables.append(self._button_return)
        else:
            self._button_return = None
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
        self._switch_lights = True

    @property
    def on_return(self):
        return self._on_return

    @on_return.setter
    def on_return(self, on_return):
        self._on_return = on_return

    def touch(self, x: int, y: int):
        if self._hidden:
            return
        for touchable in self._touchables:
            touchable.touch(x, y)

    @property
    def side_colour(self):
        return self._side_colour

    @side_colour.setter
    def side_colour(self, side_colour):
        self._side_colour = side_colour
        self.title_rectangle.fill_colour = side_colour
        if self._title_text:
            self._title_text.fill_colour = side_colour
            self._title_text.text_colour = side_colour.get_contrasting_text()
            print(self._title_text)
        self.left_bar.fill_colour = side_colour
        self.line.colour = side_colour

    def update(self):
        if self._text_round:
            self._text_round.text = f"R {self._game.round}"
        if self._text_turn:
            self._text_turn.text = f"T {self._game.turn}"
        if self._switch_lights:
            if self._side_colour in colours.PLAYER_COLOURS:
                self._lights.turn_on(self._side_colour)
            else:
                self._lights.turn_off()

    def hide(self):
        self._hidden = True

    def draw(self):
        self._hidden = False
        self.title_rectangle.draw()
        if self._title_text:
            self._title_text.draw()
        self.left_bar.draw()
        self.line.draw()
        self.background.draw()
        if self._button_return:
            self._button_return.draw()
        if self._text_round:
            self._text_round.draw()
        if self._text_turn:
            self._text_turn.draw()

    def _create_grid_players(self, button_font, players, event):
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
                    button.args = {"player": player}
                    button.action = lambda args: events.HANDLER.send_event(event, args)
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
    def __init__(
        self,
        lights: leds.Lights,
    ):
        super().__init__(
            lights, "welcome", "TI 4 assistant", colours.WHITE, has_return=False
        )
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
        self._button_setup.action = lambda args: events.HANDLER.send_event(
            events.SETUP, args
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
        self._button_play.action = lambda args: events.HANDLER.send_event(
            events.PLAY, args
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
        self._button_reset.action = lambda args: events.HANDLER.send_event(
            events.RESET, args
        )
        self._touchables.append(self._button_setup)
        self._touchables.append(self._button_play)
        self._touchables.append(self._button_reset)
        self.update()

    def draw(self):
        super().draw()
        self._button_setup.draw()
        self._button_play.draw()
        self._button_reset.draw()


class ScreenSetup(Screen):
    def __init__(self, lights: leds.Lights, players: list[Player]):
        super().__init__(lights, "setup", None, colours.WHITE)
        self._on_return = ScreenTypes.WELCOME
        self._players = players
        self._on_return = ScreenTypes.WELCOME
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
            button_font,
            players,
            events.SETUP_COLOUR,
        )
        self._touchables.extend(self._buttons)
        self.update()

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

    def __init__(self, lights: leds.Lights, players: list[Player], player_index: int):
        player = players[player_index]
        super().__init__(
            lights, "setup name", players[player_index].name + "_", colours.WHITE
        )
        self._on_return = ScreenTypes.SETUP_PLAYERS
        button_small_font = Widgets.FONTS.DejaVu12
        button_font = Widgets.FONTS.DejaVu40
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
            button_small_font,
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
            button_small_font,
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
        self._touchables.append(self._button_left)
        self._touchables.append(self._button_right)
        self._touchables.extend(self._buttons)
        self._touchables.append(self._button_erase)
        self.update()

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
    def __init__(self, lights: leds.Lights, players: list[Player], player):
        self._colours_to_players = {}
        for other_player in players:
            if other_player.colour != colours.PLAYER_BLANK:
                self._colours_to_players[other_player.colour] = other_player
        super().__init__(
            lights,
            "setup colour",
            player.name,
            title_colour=None,
            side_colour=player.colour,
        )
        self._on_return = ScreenTypes.SETUP_PLAYERS
        self._previous_colour = player.colour
        events.HANDLER.register(events.PICK_COLOUR, self)
        events.HANDLER.register_once(events.RETURN, self)
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
                highlight = False
                disable = False
                is_colour = not ((line == 1) and (column == 1))
                if is_colour:
                    colour = colours.PLAYER_COLOURS[index]
                    if colour in self._colours_to_players:
                        other_player = self._colours_to_players[colour]
                        text = other_player.name
                        if player == other_player:
                            highlight = True
                        else:
                            disable = True
                    else:
                        text = colour.pretty_name[len("player ") :]
                    index += 1
                else:
                    colour = colours.PLAYER_BLANK
                    text = "back"
                    disable = False
                control = blocks.ButtonRectangle(
                    LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                    TITLE_HEIGHT + dy + (dy + sy) * line,
                    sx,
                    sy,
                    text,
                    colour,
                    Screen.COLOUR_BORDER,
                )
                if is_colour:
                    args = {
                        "colour": colour,
                        "player": player,
                    }
                    control.args = args
                    control.action = lambda args: events.HANDLER.send_event(
                        events.PICK_COLOUR, args
                    )
                else:
                    control.action = lambda args: events.HANDLER.send_event(
                        events.RETURN, args
                    )
                if disable:
                    control.enabled = False
                if highlight:
                    control.highlighted = True
                if is_colour:
                    self._buttons.append(control)
                else:
                    self._center_control = control
        self._touchables.extend(self._buttons)
        self._touchables.append(self._center_control)
        self.update()

    def do_event(self, event, args):
        if events.PICK_COLOUR == event:
            player = args["player"]
            colour = args["colour"]
            print(f"pick colour {colour} for player {player}")
            if self._previous_colour != colours.PLAYER_BLANK:
                if self._previous_colour in self._colours_to_players:
                    del self._colours_to_players[self._previous_colour]
                else:
                    print(
                        f"bug while restoring previous colour {self._previous_colour}"
                    )
            self._colours_to_players[colour] = colour
            for button in self._buttons:
                if button.fill_colour == colour:
                    button.text = player.name
                    button.highlighted = True
                elif button.fill_colour == self._previous_colour:
                    button.text = self._previous_colour.pretty_name[len("player ") :]
                    button.highlighted = False
            self._previous_colour = colour
            self.side_colour = colour
            self.draw()
        elif events.RETURN == event:
            events.HANDLER.unregister(events.PICK_COLOUR, self)

    def draw(self):
        super().draw()
        for button in self._buttons:
            button.draw()
        self._center_control.draw()


class ScreenStrategy(Screen):
    def __init__(self, lights: leds.Lights, game: logic.Game):
        super().__init__(
            lights,
            "strategy",
            None,
            colours.WHITE,
            side_colour=None,
            game=game,
            has_round=True,
        )
        self._on_return = ScreenTypes.MENU
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
        self._button_end_phase.action = lambda args: events.HANDLER.send_event(
            events.NEXT, args
        )
        self._buttons, self._rectangles = self._create_grid_players(
            button_font, self._players, events.STRATEGY_PLAYER
        )
        for button, player in zip(self._buttons, self._players):
            button.add_more_text(Strategies.to_short_string(player.strategy))
        self._touchables.append(self._button_end_phase)
        self._touchables.extend(self._buttons)
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


class ScreenStrategyPlayer(Screen):
    def __init__(self, lights: leds.Lights, game: logic.Game, player_num: int):
        strategies_to_players = {}
        can_swap = True
        for player in game.players:
            if player.strategy != Strategies.NONE:
                strategies_to_players[player.strategy] = player
            else:
                can_swap = False
        player = game.get_player(player_num)
        super().__init__(
            lights,
            "strategy player",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        self._on_return = ScreenTypes.STRATEGY_MAIN
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
                args = None
                if is_colour:
                    colour = Strategies.to_colour(strategy_index)
                    is_button = True
                    if strategy_index in strategies_to_players:
                        other_player = strategies_to_players[strategy_index]
                        text = other_player.name
                        if other_player == player:
                            disable = True
                        else:
                            disable = not can_swap
                        args = {
                            "player": other_player,
                            "strategy": strategy_index,
                        }
                    else:
                        text = f"{strategy_index} [{game.available_strategies[strategy_index]}]"
                        disable = can_swap
                        args = {
                            "strategy": strategy_index,
                        }
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
                    control.args = args
                    control.action = lambda args: events.HANDLER.send_event(
                        events.PICK_STRATEGY, args
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
        for button, strategy in zip(self._buttons, logic.Strategies.ALL):
            button.add_more_text(Strategies.to_string(strategy))
        self._touchables.extend(self._buttons)
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

    def __init__(self, lights: leds.Lights, game: logic.Game):
        # game.current_player seems better then game.get_player(index)
        player = game.current_player
        super().__init__(
            lights,
            "action",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        self._on_return = ScreenTypes.MENU
        button_font = Widgets.FONTS.DejaVu12
        x_weight_player_button = 2.5
        x_weight_action_button = 3
        x_ratio_player_button = x_weight_player_button / (
            x_weight_player_button * 2 + x_weight_action_button
        )
        player_button_sx = int(x_ratio_player_button * (INNER_X + 1))
        action_button_sx = (INNER_X + 1) - 2 * player_button_sx
        small_button_height = (INNER_Y + 1) // 3 + 1

        text_previous = "previous"
        self._button_previous = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_previous,
            player.previous.colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_previous.action = lambda args: events.HANDLER.send_event(
            events.PREVIOUS, args
        )
        self._button_previous.add_more_text(player.previous.name)

        text_next = "next"
        self._button_next = blocks.ButtonRectangle(
            MAX_X - player_button_sx,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_next,
            player.next.colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_next.action = lambda args: events.HANDLER.send_event(
            events.NEXT, args
        )
        self._button_next.add_more_text(player.next.name)

        self._button_strategy = blocks.ButtonRectangle(
            self._button_previous.right - 1,
            TITLE_HEIGHT,
            self._button_next.left - self._button_previous.right + 2,
            small_button_height,
            Strategies.to_string(player.strategy),
            Strategies.to_colour(player.strategy),
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_strategy.action = lambda args: events.HANDLER.send_event(
            events.PLAY_STRATEGY, args
        )

        self._button_tactical_and_component = blocks.ButtonRectangle(
            self._button_previous.right - 1,
            self._button_strategy.bottom - 1,
            self._button_next.left - self._button_previous.right + 2,
            small_button_height,
            "Tactical",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_tactical_and_component.action = (
            lambda args: events.HANDLER.send_event(
                events.PLAY_TACTICAL_ORCOMPONENT, args
            )
        )
        self._button_tactical_and_component.add_more_text("/")
        self._button_tactical_and_component.add_more_text("Component")

        if player.can_pass:
            skip_or_pass = "Pass"
            event = events.PLAY_PASS
        else:
            skip_or_pass = "Skip"
            event = events.PLAY_SKIP
        self._button_skip_or_pass = blocks.ButtonRectangle(
            self._button_previous.right - 1,
            self._button_tactical_and_component.bottom - 1,
            self._button_next.left - self._button_previous.right + 2,
            MAX_Y - (self._button_tactical_and_component.bottom - 1),
            skip_or_pass,
            colours.GRAY,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_tactical_and_component.action = (
            lambda args: events.HANDLER.send_event(event, args)
        )
        self._touchables.append(self._button_previous)
        self._touchables.append(self._button_next)
        self._touchables.append(self._button_strategy)
        self._touchables.append(self._button_tactical_and_component)
        self._touchables.append(self._button_skip_or_pass)
        self.update()

    def draw(self):
        super().draw()
        self._button_previous.draw()
        self._button_next.draw()
        self._button_strategy.draw()
        self._button_tactical_and_component.draw()
        self._button_skip_or_pass.draw()


class ScreenStatus(Screen):
    """
    The custom part should look like this
    <---------- INNER_X ---------->
    +-------+---+-----+---+-------+   ^
    |       |             |       |   |
    |       |             |       |   |
    |       |             |       |   |
    +       +             +       +   |
    |Previou|             | Next  |
    |       |    TEXT     |       | INNER_Y
    |player |             |player |
    +       +             +       +   |
    |       |             |       |   |
    |       |             |       |   |
    |       |             |       |   |
    +-------+---+-----+---+-------+   v
      2.5         3.0        2.5
    Maybe a bit of spacing between the buttons if possible.
    """

    def __init__(self, lights: leds.Lights, game: logic.Game):
        # game.current_player seems better then game.get_player(index)
        player = game.current_player
        super().__init__(
            lights,
            "action",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        self._on_return = ScreenTypes.MENU
        button_font = Widgets.FONTS.DejaVu12
        x_weight_player_button = 2.5
        x_weight_action_button = 3
        x_ratio_player_button = x_weight_player_button / (
            x_weight_player_button * 2 + x_weight_action_button
        )
        player_button_sx = int(x_ratio_player_button * (INNER_X + 1))
        action_button_sx = (INNER_X + 1) - 2 * player_button_sx
        small_button_height = (INNER_Y + 1) // 3 + 1

        text_previous = "previous"
        self._button_previous = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_previous,
            player.previous.colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_previous.action = lambda args: events.HANDLER.send_event(
            events.PREVIOUS, args
        )
        self._button_previous.add_more_text(player.previous.name)

        text_next = "next"
        self._button_next = blocks.ButtonRectangle(
            MAX_X - player_button_sx,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_next,
            player.next.colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_next.action = lambda args: events.HANDLER.send_event(
            events.NEXT, args
        )
        self._button_next.add_more_text(player.next.name)

        y_offset = 30
        self._description = blocks.Rectangle(
            self._button_previous.right - 1,
            TITLE_HEIGHT + y_offset,
            self._button_next.left - self._button_previous.right + 2,
            INNER_Y + 1 - y_offset * 2,
            "Score",
            colours.PALETTE_DARK_BLUE,
            colours.PALETTE_DARK_BLUE,
            Widgets.FONTS.DejaVu18,
        )
        self._description.add_more_text("at most")
        self._description.add_more_text("one of each")
        self._description.add_more_text("type of")
        self._description.add_more_text("objective")
        self._description.add_more_text("(public,")
        self._description.add_more_text("private)")

        self._touchables.append(self._button_previous)
        self._touchables.append(self._button_next)
        self.update()

    def draw(self):
        super().draw()
        self._button_previous.draw()
        self._button_next.draw()
        self._description.draw()


class ScreenMenu(Screen):
    def __init__(
        self,
        lights: leds.Lights,
    ):
        super().__init__(
            lights, "menu", "TI 4 assistant", colours.WHITE, has_return=True
        )
        self._on_return = ScreenTypes.SAVED_SCREEN
        button_sx = 150
        button_sy = 65
        button_x_delta = (MAX_X - (LEFT_BAR_WIDTH + 1) - button_sx) // 2
        button_x_offset = LEFT_BAR_WIDTH + 1 + button_x_delta
        dx = 4
        dy = 4
        button_font = Widgets.FONTS.DejaVu18
        self._button_welcome = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy,
            button_sx,
            button_sy,
            "Welcome",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        self._button_welcome.action = lambda args: events.HANDLER.send_event(
            events.WELCOME, args
        )
        self._button_reset_phase = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy + button_sy + dy,
            button_sx,
            button_sy,
            "Reset phase",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        self._button_reset_phase.action = lambda args: events.HANDLER.send_event(
            events.RESET_PHASE, args
        )
        self._button_reset_round = blocks.ButtonRectangle(
            button_x_offset,
            TITLE_HEIGHT + dy + (button_sy + dy) * 2,
            button_sx,
            button_sy,
            "Reset round",
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
        )
        self._button_reset_round.action = lambda args: events.HANDLER.send_event(
            events.RESET_ROUND, args
        )
        self._switch_lights = False
        self._touchables.append(self._button_welcome)
        self._touchables.append(self._button_reset_phase)
        self._touchables.append(self._button_reset_round)
        self.update()

    def draw(self):
        super().draw()
        self._button_welcome.draw()
        self._button_reset_phase.draw()
        self._button_reset_round.draw()


def main(select=None):
    import sys
    import M5
    import logic

    from M5 import Speaker

    select = 1
    if not device.is_micropython():
        M5.begin()
        if len(sys.argv) > 1:
            try:
                param = int(sys.argv[1])
                if 0 < param <= 16:
                    select = param
            except:
                pass
    else:
        Speaker.setVolume(15)
    Speaker.tone(2000, 50)
    lights = leds.Lights(only_print=True)
    if 1 == select:
        screen_welcome = ScreenWelcome(lights)
        screen_welcome.draw()
        screen_welcome._button_setup.force_touch()
    elif 2 == select:
        game = logic.Game.build_fake_game()
        screen_setup = ScreenSetup(lights, game.players)
        screen_setup.draw()
    elif 3 == select:
        game = logic.Game()
        screen_setup = ScreenSetup(lights, game.players)
        screen_setup.draw()
    elif 4 == select:
        game = logic.Game.build_fake_game()
        screen_setup_name = ScreenSetupName(lights, game.players, 2)
        screen_setup_name.draw()
    elif 5 == select:
        game = logic.Game()
        screen_setup_name = ScreenSetupName(lights, game.players, 2)
        screen_setup_name.draw()
    elif 6 == select:
        game = logic.Game.build_fake_game()
        screen_setup_colour = ScreenSetupColour(lights, game.players, game.players[4])
        screen_setup_colour.draw()
    elif 7 == select:
        game = logic.Game()
        screen_setup_colour = ScreenSetupColour(lights, game.players, game.players[4])
        screen_setup_colour.draw()
    elif 8 == select:
        game = logic.Game()
        player = game.get_player(2)
        player.name = "Pierre"
        player.colour = colours.PLAYER_BLACK
        screen_setup_colour = ScreenSetupColour(lights, game.players, game.players[4])
        screen_setup_colour.draw()
    elif 9 == select:
        game = logic.Game.build_fake_game()
        screen_setup_colour = ScreenStrategy(lights, game)
        screen_setup_colour.draw()
    elif 10 == select:
        game = logic.Game.build_fake_game()
        game.start_playing()
        player = game.get_next_player()
        player.strategy = Strategies.WARFARE
        player = game.get_next_player()
        player.strategy = Strategies.TECHNOLOGY
        screen_setup_colour = ScreenStrategy(lights, game)
        screen_setup_colour.draw()
    elif 11 == select:
        game = logic.Game.build_fake_game()
        game.start_playing()
        screen_setup_colour = ScreenStrategyPlayer(lights, game, player_num=5)
        screen_setup_colour.draw()
    elif 12 == select:
        game = logic.Game.build_fake_game()
        game.start_playing()
        player = game.get_next_player()
        player.strategy = Strategies.WARFARE
        player = game.get_next_player()
        player.strategy = Strategies.TECHNOLOGY
        screen_setup_colour = ScreenStrategyPlayer(lights, game, player_num=5)
        screen_setup_colour.draw()
    elif 13 <= select <= 15:
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
            screen_strategy_player = ScreenStrategyPlayer(lights, game, player.num)
            screen_strategy_player.draw()
        elif 14 == select:
            screen_action = ScreenAction(lights, game)
            screen_action.draw()
        elif 15 == select:
            screen_status = ScreenStatus(lights, game)
            screen_status.draw()
    elif 16 == select:
        screen_menu = ScreenMenu(lights)
        screen_menu.draw()
    if not device.is_micropython():
        while True:
            M5.update()


if "__main__" == __name__:
    main()
