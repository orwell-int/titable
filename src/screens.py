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
    # 3 x 2 for players
    #  first round: third row is yes / no
    #  other rounds (only if yes): previous / next
    NAALU_ABILITY = 4
    # players 2 x 3 (with selected strategy) with button to end strategy phase
    # (button only enabled when every player has picked)
    # shows round (and turn) in left bar
    STRATEGY_MAIN = 5
    # player dedicated 3 x 3 buttons (number [trade goods] -> name)
    # add swap option in the middle when every player has picked something
    # shows round (and turn) in left bar
    STRATEGY_PLAYER = 6
    # player dedicated three vertical buttons to chose type of action + one for next (player / phase)
    # should it include one button to go back to previous?
    # shows round and turn in left bar
    ACTION_PLAYER = 7
    # One button to go back to previous phase, one to go to next phase
    # same as status, but for all
    AGENDA = 8
    # player dedicated one button for previous + text + one for next (player / round)
    STATUS_PLAYER = 9
    # Menu
    MENU = 10
    # Screen opened before the menu
    SAVED_SCREEN = 11
    # Select the number of players
    NUM_PLAYERS = 99


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


class DelaySendEvent:
    def __init__(self, event, debug=False):
        self._event = event
        self._debug = debug

    def __call__(self, sender, args):
        if self._debug:
            print(f"call {sender} {self} {args}")
        events.HANDLER.send_event(sender, self._event, args)

    def __str__(self):
        return f"<{events.to_string(self._event)}>"


class Screen:
    COLOUR_BORDER = colours.PALETTE_GOLD

    def __init__(
        self,
        lights: leds.Lights,
        screen_type: int,
        name,
        title,
        title_colour,
        side_colour=None,
        has_return=True,
        game=None,
        has_round=False,
        has_turn=False,
    ):
        self._lights = lights
        self._screen_type = screen_type
        self.name = name
        self.title = title
        if side_colour is None:
            side_colour = colours.PALETTE_DARK_GREEN
        if title_colour is not None:
            self.title_colour = title_colour
        else:
            self.title_colour = side_colour.get_contrasting_text()
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
            self._button_return.action = DelaySendEvent(events.RETURN)
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
    def screen_type(self):
        return self._screen_type

    @property
    def on_return(self):
        return self._on_return

    @on_return.setter
    def on_return(self, on_return):
        events.HANDLER.register_once(events.RETURN, self)
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
        if self._side_colour == side_colour:
            return
        self._side_colour = side_colour
        self.title_rectangle.fill_colour = side_colour
        if self._title_text:
            self._title_text.fill_colour = side_colour
            self._title_text.text_colour = side_colour.get_contrasting_text()
            # print(self._title_text)
        self.left_bar.fill_colour = side_colour
        self.line.colour = side_colour
        if self._switch_lights:
            if self._side_colour in colours.PLAYER_COLOURS:
                self._lights.turn_on(self._side_colour)
            else:
                self._lights.turn_on(colours.PLAYER_NEUTRAL)
                # self._lights.turn_off()

    def update(self):
        if self._text_round:
            self._text_round.text = f"R {self._game.round}"
        if self._text_turn:
            self._text_turn.text = f"T {self._game.turn}"
        if self._switch_lights:
            if self._side_colour in colours.PLAYER_COLOURS:
                self._lights.turn_on(self._side_colour)
            else:
                # self._lights.turn_off()
                self._lights.turn_on(colours.PLAYER_NEUTRAL)

    def do_event(self, sender, event, args):
        pass

    def hide(self):
        self._hidden = True
        events.HANDLER.unregister(events.ALL, self)

    def draw(self):
        self._hidden = False
        self.title_rectangle.draw()
        if self._title_text:
            self._title_text.draw()
        drawn_left_bar = self.left_bar.draw()
        self.line.draw()
        self.background.draw()
        if self._button_return:
            self._button_return.draw(force_changed=drawn_left_bar)
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
                    button.action = DelaySendEvent(event)
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
        game: logic.Game,
    ):
        super().__init__(
            lights,
            ScreenTypes.WELCOME,
            "welcome",
            "TI 4 assistant",
            colours.WHITE,
            has_return=False,
        )
        self._game = game
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
        self._button_setup.action = DelaySendEvent(events.SETUP)
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
        self._button_play.action = DelaySendEvent(events.PLAY)
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
        self._button_reset.action = DelaySendEvent(events.RESET)
        self._touchables.append(self._button_setup)
        self._touchables.append(self._button_play)
        self._touchables.append(self._button_reset)
        self.update()

    def update(self):
        super().update()
        self._button_play.enabled = self._game.players_ready_to_play

    def draw(self):
        super().draw()
        self._button_setup.draw()
        self._button_play.draw()
        self._button_reset.draw()


class ScreenSetup(Screen):
    def __init__(self, lights: leds.Lights, players: list[Player]):
        super().__init__(
            lights, ScreenTypes.SETUP_PLAYERS, "setup", None, colours.WHITE
        )
        self._players = players
        self.on_return = ScreenTypes.WELCOME
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
            lights,
            ScreenTypes.SETUP_PLAYER_NAME,
            "setup name",
            players[player_index].name + "_",
            colours.WHITE,
        )
        self.on_return = ScreenTypes.SETUP_PLAYERS
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
            ScreenTypes.SETUP_PLAYER_COLOUR,
            "setup colour",
            player.name,
            title_colour=None,
            side_colour=player.colour,
        )
        self.on_return = ScreenTypes.SETUP_PLAYERS
        self._previous_colour = player.colour
        self._player = player
        events.HANDLER.register(events.PICK_COLOUR, self)
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
                    control.action = DelaySendEvent(events.PICK_COLOUR)
                else:
                    control.action = DelaySendEvent(events.RETURN)
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
        self._switch_lights = True
        self.update()

    def do_event(self, sender, event, args):
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
        # elif events.RETURN == event:
        #     events.HANDLER.unregister(events.PICK_COLOUR, self)

    def hide(self):
        super().hide()
        self._player.write_colour()

    def draw(self):
        super().draw()
        for button in self._buttons:
            button.draw()
        self._center_control.draw()


class ScreenNaaluAbility(Screen):
    def __init__(self, lights: leds.Lights, game: logic.Game):
        super().__init__(
            lights,
            ScreenTypes.NAALU_ABILITY,
            "naalu",
            None,
            colours.WHITE,
            side_colour=None,
            game=game,
            has_round=True,
        )
        self.on_return = ScreenTypes.MENU


class ScreenStrategy(Screen):
    def __init__(self, lights: leds.Lights, game: logic.Game):
        super().__init__(
            lights,
            ScreenTypes.STRATEGY_MAIN,
            "strategy",
            None,
            colours.WHITE,
            side_colour=None,
            game=game,
            has_round=True,
        )
        # self.on_return = ScreenTypes.NAALU_ABILITY
        self.on_return = ScreenTypes.WELCOME
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
        self._button_end_phase.action = DelaySendEvent(events.NEXT)
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
        self._strategies_to_players = {}
        can_swap = True
        for player in game.players:
            if player.strategy != Strategies.NONE:
                self._strategies_to_players[player.strategy] = player
            else:
                can_swap = False
        self._other_player = None
        self._other_strategy = None
        self._other_button = None
        self._player_button = None
        self._player = game.get_player(player_num)
        self._previous_strategy = self._player.strategy
        super().__init__(
            lights,
            ScreenTypes.STRATEGY_PLAYER,
            "strategy player",
            self._player.name,
            title_colour=None,
            side_colour=self._player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        self.on_return = ScreenTypes.STRATEGY_MAIN
        events.HANDLER.register(events.PICK_STRATEGY, self)
        events.HANDLER.register(events.PICK_STRATEGY_SWAP, self)
        events.HANDLER.register(events.UNPICK_STRATEGY_SWAP, self)
        events.HANDLER.register(events.SWAP_STRATEGY, self)
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
                event = None
                is_for_current_player = False
                if is_colour:
                    colour = Strategies.to_colour(strategy_index)
                    text = f"{strategy_index} [{game.available_strategies[strategy_index]}]"
                    if strategy_index in self._strategies_to_players:
                        other_player = self._strategies_to_players[strategy_index]
                        if other_player == self._player:
                            other_player = None
                            is_for_current_player = True
                            disable = True
                        else:
                            disable = not can_swap
                    else:
                        other_player = None
                    control = blocks.ButtonRectangle(
                        LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                        TITLE_HEIGHT + dy + (dy + sy) * line,
                        sx,
                        sy,
                        text,
                        colour,
                        Screen.COLOUR_BORDER,
                    )
                    if is_for_current_player:
                        self._player_button = control
                    # print(f"Disable at column {column}, line {line} ?", disable)
                    if disable:
                        control.enabled = False
                    if other_player is not None:
                        event = events.PICK_STRATEGY_SWAP
                        args = {
                            "other_strategy": strategy_index,
                            "other_player": other_player,
                            "line": line,
                            "column": column,
                            "event": events.to_string(event),
                        }
                    else:
                        event = events.PICK_STRATEGY
                        args = {
                            "strategy": strategy_index,
                            "line": line,
                            "column": column,
                            "event": events.to_string(event),
                        }
                    control.args = args
                    control.action = DelaySendEvent(event)
                    # print(f"At column {column}, line {line} event {events.to_string(event)} args {args}")
                    self._buttons.append(control)
                    strategy_index += 1
                else:
                    colour = colours.PLAYER_BLANK
                    text = "back"
                    control = blocks.ButtonRectangle(
                        LEFT_BAR_WIDTH + dx + (dx + sx) * column,
                        TITLE_HEIGHT + dy + (dy + sy) * line,
                        sx,
                        sy,
                        text,
                        colour,
                        Screen.COLOUR_BORDER,
                    )
                    control.action = DelaySendEvent(events.RETURN)
                    self._center_control = control
        for button, strategy in zip(self._buttons, logic.Strategies.ALL):
            button.add_more_text(Strategies.to_string(strategy))
            if strategy in self._strategies_to_players:
                player = self._strategies_to_players[strategy]
                button.add_more_text(player.name)
            else:
                button.add_more_text("")
            # print("button.action:", button.action)
            # print("button.args:", button.args)
        self._touchables.extend(self._buttons)
        self._touchables.append(self._center_control)
        self.update()

    def do_event(self, sender, event, args):
        # print(f"do_event {events.to_string(event)} {args}")
        if events.PICK_STRATEGY == event:
            strategy = args["strategy"]
            print(f"pick strategy {strategy} for player {self._player}")
            if self._previous_strategy != logic.Strategies.NONE:
                if self._previous_strategy in self._strategies_to_players:
                    del self._strategies_to_players[self._previous_strategy]
                else:
                    print(
                        f"bug while restoring previous strategy {self._previous_strategy}"
                    )
            self._strategies_to_players[strategy] = self._player
            previous_colour = logic.Strategies.to_colour(self._previous_strategy)
            colour = logic.Strategies.to_colour(strategy)
            # print(f"previous_colour = {previous_colour} ; colour = {colour}")
            for button in self._buttons:
                if button.fill_colour == colour:
                    button.set_more_text(1, self._player.name)
                    button.highlighted = True
                    button.enabled = False
                    self._player_button = button
                elif button.fill_colour == previous_colour:
                    button.set_more_text(1, "")
                    button.highlighted = False
                    button.enabled = True
            self._previous_strategy = strategy
            self.side_strategy = strategy
            self._player.strategy = strategy
            self.draw()
        elif events.PICK_STRATEGY_SWAP == event:
            self._other_player = args["other_player"]
            self._other_strategy = args["other_strategy"]
            self._other_button = sender
            self._player_button.highlighted = False
            button = sender
            button.enabled = True
            button.highlighted = True
            button.action = DelaySendEvent(events.UNPICK_STRATEGY_SWAP)
            for other_button in self._buttons:
                if button != other_button:
                    other_button.enabled = False
            self._center_control.text = "swap"
            self._center_control.action = DelaySendEvent(events.SWAP_STRATEGY)
            self.draw()
        elif events.UNPICK_STRATEGY_SWAP == event:
            button = sender
            button.highlighted = False
            button.action = DelaySendEvent(events.PICK_STRATEGY_SWAP)
            self._center_control.text = "back"
            self._center_control.action = DelaySendEvent(events.RETURN)
            for other_button in self._buttons:
                if self._player_button != other_button:
                    other_button.enabled = True
            self._other_player = None
            self._other_strategy = None
            self._other_button = None
            self.draw()
        elif events.SWAP_STRATEGY == event:
            # swap strategies in mapping
            self._strategies_to_players[self._other_player.strategy] = self._player
            self._strategies_to_players[self._player.strategy] = self._other_player
            # swap stratgies in players
            self._other_player.strategy = self._player.strategy
            self._player.strategy = self._other_strategy
            # swap players in buttons
            self._other_button.set_more_text(1, self._player.name)
            self._player_button.set_more_text(1, self._other_player.name)
            # fix various states
            self._player_button.args = {
                "other_strategy": self._other_player.strategy,
                "other_player": self._other_player,
            }
            self._player_button.action = DelaySendEvent(events.PICK_STRATEGY_SWAP)
            # Make the player button the one that was picked for swapping
            self._player_button = self._other_button
            self._player_button.args = {
                "strategy": self._player.strategy,
            }
            self._player_button.action = DelaySendEvent(events.PICK_STRATEGY)
            self._player_button.enabled = False
            self._player_button.highlighted = True
            self._center_control.text = "back"
            self._center_control.action = DelaySendEvent(events.RETURN)
            self._other_player = None
            self._other_strategy = None
            self._other_button = None
            for other_button in self._buttons:
                if self._player_button != other_button:
                    other_button.enabled = True
            self._previous_strategy = self._player.strategy
            self.draw()
        # elif events.RETURN == event:
        #     events.HANDLER.unregister(events.ALL, self)

    def draw(self):
        super().draw()
        for button in self._buttons:
            button.draw()
        self._center_control.draw()

    def hide(self):
        super().hide()
        self._player.write_strategy()


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
        player_previous = game.previous_player
        player_next = game.next_player
        super().__init__(
            lights,
            ScreenTypes.ACTION_PLAYER,
            "action",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=True,
        )
        self._game = game
        self.on_return = ScreenTypes.MENU
        self._highlighted = None
        self._is_last_player = player_next == player
        events.HANDLER.register(events.PLAY_STRATEGY, self)
        events.HANDLER.register(events.PLAY_TACTICAL_OR_COMPONENT, self)
        events.HANDLER.register(events.PLAY_SKIP, self)
        events.HANDLER.register(events.PLAY_PASS, self)
        events.HANDLER.register(events.NEXT, self)
        button_font = Widgets.FONTS.DejaVu12
        x_weight_player_button = 2.5
        x_weight_action_button = 3
        x_ratio_player_button = x_weight_player_button / (
            x_weight_player_button * 2 + x_weight_action_button
        )
        player_button_sx = int(x_ratio_player_button * (INNER_X + 1))
        action_button_sx = (INNER_X + 1) - 2 * player_button_sx
        small_button_height = (INNER_Y + 1) // 3 + 1

        game.print_player_nums("ScreenAction")
        if not player_next:
            raise Exception("No next player!")

        if player_previous:
            colour = player_previous.colour
            text_previous = "previous"
        else:
            colour = colours.PALETTE_LIGHT_GREEN
            text_previous = "Strategy"
        self._button_previous = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_previous,
            colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_previous.action = DelaySendEvent(events.PREVIOUS)
        if player_previous:
            self._button_previous.add_more_text(player_previous.name)
            self._button_previous.args = {"phase": logic.Game.PHASE_ACTION}
        else:
            self._button_previous.add_more_text("phase")
            self._button_previous.args = {"phase": logic.Game.PHASE_STRATEGY}

        text_next = "next"
        self._button_next = blocks.ButtonRectangle(
            MAX_X - player_button_sx,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_next,
            player_next.colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_next.action = DelaySendEvent(events.NEXT)
        self._button_next.add_more_text(player_next.name)
        self._button_next.enabled = False

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
        self._button_strategy.action = DelaySendEvent(events.PLAY_STRATEGY)
        if player.has_played_strategy:
            self._button_strategy.enabled = False

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
        self._button_tactical_and_component.action = DelaySendEvent(
            events.PLAY_TACTICAL_OR_COMPONENT
        )
        self._button_tactical_and_component.add_more_text("/")
        self._button_tactical_and_component.add_more_text("Component")

        if player.can_pass:
            skip_or_pass = "Pass"
            event = events.PLAY_PASS
            is_skip = False
        else:
            skip_or_pass = "Skip"
            event = events.PLAY_SKIP
            is_skip = True
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
        if is_skip and self._is_last_player:
            self._button_skip_or_pass.enabled = False
        self._selected_pass = False
        self._button_skip_or_pass.action = DelaySendEvent(event)
        self._touchables.append(self._button_previous)
        self._touchables.append(self._button_next)
        self._touchables.append(self._button_strategy)
        self._touchables.append(self._button_tactical_and_component)
        self._touchables.append(self._button_skip_or_pass)
        self.update()

    def _highlight(self, item):
        if self._highlighted == item:
            return
        if self._highlighted is not None:
            self._highlighted.highlighted = False
        self._highlighted = item
        if item is None:
            self._button_next.enabled = False
        else:
            item.highlighted = True
            self._button_next.enabled = True

    def _toggle_next_text(self, end_phase):
        if end_phase:
            self._button_next.text = "Agenda"
            self._button_next.set_more_text(0, "phase")
            self._button_next.fill_colour = colours.PALETTE_LIGHT_BLUE
        else:
            self._button_next.text = "next"
            self._button_next.set_more_text(0, self._game.current_player.name)
            self._button_next.fill_colour = self._game.current_player.colour

    def do_event(self, sender, event, args):
        print(f"do_event {events.to_string(event)} {args}")
        if events.PLAY_STRATEGY == event:
            self._highlight(sender)
            self.draw()
        elif events.PLAY_TACTICAL_OR_COMPONENT == event:
            self._highlight(sender)
            if self._is_last_player:
                self._toggle_next_text(end_phase=False)
            self.draw()
        elif events.PLAY_PASS == event:
            self._highlight(sender)
            if self._is_last_player:
                self._toggle_next_text(end_phase=True)
            self._selected_pass = True
            self.draw()
        elif events.PLAY_SKIP == event:
            self._highlight(sender)
            self.draw()

    def draw(self):
        super().draw()
        self._button_previous.draw()
        self._button_next.draw()
        self._button_strategy.draw()
        self._button_tactical_and_component.draw()
        self._button_skip_or_pass.draw()


class ScreenAgenda(Screen):
    def __init__(
        self,
        lights: leds.Lights,
        game: logic.Game,
    ):
        super().__init__(
            lights,
            ScreenTypes.AGENDA,
            "agenda",
            "Agenda",
            colours.WHITE,
        )
        print("ScreenAgenda")
        self._game = game
        self.on_return = ScreenTypes.MENU
        button_font = Widgets.FONTS.DejaVu12
        x_weight_player_button = 2.5
        x_weight_action_button = 3
        x_ratio_player_button = x_weight_player_button / (
            x_weight_player_button * 2 + x_weight_action_button
        )
        player_button_sx = int(x_ratio_player_button * (INNER_X + 1))
        action_button_sx = (INNER_X + 1) - 2 * player_button_sx
        small_button_height = (INNER_Y + 1) // 3 + 1

        text_previous = "Action"
        self._button_previous = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_previous,
            colours.PALETTE_LIGHT_GREEN,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_previous.action = DelaySendEvent(events.PREVIOUS)
        self._button_previous.args = {"phase": logic.Game.PHASE_ACTION}
        self._button_previous.add_more_text("phase")

        text_next = "Status"
        self._button_next = blocks.ButtonRectangle(
            MAX_X - player_button_sx,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_next,
            colours.PALETTE_LIGHT_BLUE,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_next.action = DelaySendEvent(events.NEXT)
        self._button_next.add_more_text("phase")

        y_offset = 30
        self._description = blocks.Rectangle(
            self._button_previous.right - 1,
            TITLE_HEIGHT + y_offset,
            self._button_next.left - self._button_previous.right + 2,
            INNER_Y + 1 - y_offset * 2,
            "Perform",
            colours.PALETTE_DARK_BLUE,
            colours.PALETTE_DARK_BLUE,
            Widgets.FONTS.DejaVu18,
        )
        self._description.add_more_text("agenda")
        self._description.add_more_text("phase")
        self._description.add_more_text("if")
        self._description.add_more_text("Mecatol")
        self._description.add_more_text("was")
        self._description.add_more_text("captured")

        self._touchables.append(self._button_previous)
        self._touchables.append(self._button_next)
        self.update()

    def draw(self):
        super().draw()
        self._button_previous.draw()
        self._button_next.draw()
        self._description.draw()


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
        player_previous = game.previous_player
        player_next = game.next_player
        super().__init__(
            lights,
            ScreenTypes.STATUS_PLAYER,
            "action",
            player.name,
            title_colour=None,
            side_colour=player.colour,
            game=game,
            has_round=True,
            has_turn=False,
        )
        self._game = game
        self.on_return = ScreenTypes.MENU
        button_font = Widgets.FONTS.DejaVu12
        x_weight_player_button = 2.5
        x_weight_action_button = 3
        x_ratio_player_button = x_weight_player_button / (
            x_weight_player_button * 2 + x_weight_action_button
        )
        player_button_sx = int(x_ratio_player_button * (INNER_X + 1))
        action_button_sx = (INNER_X + 1) - 2 * player_button_sx
        small_button_height = (INNER_Y + 1) // 3 + 1

        if player_previous:
            colour = player_previous.colour
            text_previous = "previous"
        else:
            colour = colours.PALETTE_LIGHT_GREEN
            text_previous = "agenda"
        self._button_previous = blocks.ButtonRectangle(
            LEFT_BAR_WIDTH,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_previous,
            colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_previous.action = DelaySendEvent(events.PREVIOUS)
        if player_previous:
            self._button_previous.add_more_text(player_previous.name)
        else:
            self._button_previous.add_more_text("phase")

        text_next = "next"
        if player_next:
            colour = player_next.colour
        else:
            colour = colours.PALETTE_LIGHT_GREEN
        self._button_next = blocks.ButtonRectangle(
            MAX_X - player_button_sx,
            TITLE_HEIGHT,
            player_button_sx,
            INNER_Y + 1,
            text_next,
            colour,
            Screen.COLOUR_BORDER,
            button_font,
            inset=2,
        )
        self._button_next.action = DelaySendEvent(events.NEXT)
        if player_next:
            self._button_next.add_more_text(player_next.name)
        else:
            self._button_next.add_more_text("round")

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
            lights,
            ScreenTypes.MENU,
            "menu",
            "TI 4 assistant",
            colours.WHITE,
        )
        self.on_return = ScreenTypes.SAVED_SCREEN
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
        self._button_welcome.action = DelaySendEvent(events.WELCOME, debug=True)
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
        self._button_reset_phase.action = DelaySendEvent(events.RESET_PHASE)
        self._button_reset_phase.enabled = False
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
        self._button_reset_round.action = DelaySendEvent(events.RESET_ROUND)
        self._button_reset_round.enabled = False
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


class ScreenNumPlayer(Screen):
    def __init__(
        self,
        lights: leds.Lights,
    ):
        super().__init__(
            lights,
            ScreenTypes.NUM_PLAYERS,
            "num players",
            "How many players?",
            title_colour=None,
            side_colour=None,
            game=None,
            has_round=False,
            has_turn=False,
            has_return=False,
        )
        button_font = Widgets.FONTS.DejaVu18
        dy = 4
        top_button_sy = TITLE_HEIGHT - dy * 2
        top_button_sx = 180
        delta_x = (MAX_X - LEFT_BAR_WIDTH - top_button_sx) // 2
        self._buttons, self._rectangles = self._create_grid_numbers(
            button_font, events.SELECT_NUM_PLAYERS
        )
        self._touchables.extend(self._buttons)
        self.update()

    def _create_grid_numbers(self, button_font, event):
        num_columns = 2
        num_lines = 3
        button_sx = (INNER_X + 2) // num_columns
        button_sy = (INNER_Y + 2) // num_lines
        max_num_players = 6
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
                if index < max_num_players:
                    num = index + 1
                    button = blocks.ButtonRectangle(
                        x,
                        y,
                        sx,
                        sy,
                        str(num),
                        colours.STRATEGY_COLOURS[index],
                        Screen.COLOUR_BORDER,
                        button_font,
                    )
                    button.args = {"num_players": num}
                    button.action = DelaySendEvent(event)
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

    def update(self):
        super().update()

    def draw(self):
        super().draw()
        for button in self._buttons:
            button.draw()
        for rectangle in self._rectangles:
            rectangle.draw()


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
                if 0 < param <= 18:
                    select = param
            except:
                pass
    else:
        Speaker.setVolume(15)
    Speaker.tone(2000, 50)
    lights = leds.Lights(only_print=True)
    if 1 == select:
        game = logic.Game.build_fake_game()
        screen_welcome = ScreenWelcome(lights, game)
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
    elif 17 == select:
        game = logic.Game.build_fake_game()
        screen_menu = ScreenAgenda(lights, game)
        screen_menu.draw()
    elif 18 == select:
        screen_menu = ScreenNumPlayer(lights)
        screen_menu.draw()
    if not device.is_micropython():
        while True:
            M5.update()


if "__main__" == __name__:
    main()
