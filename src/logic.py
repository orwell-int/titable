import os

import colours
from colours import Colour
import device


USE_UNICODE = False


class Strategies:
    NONE = 0
    LEADERSHIP = 1
    DIPLOMACY = 2
    POLITICS = 3
    CONSTRUCTION = 4
    TRADE = 5
    WARFARE = 6
    TECHNOLOGY = 7
    IMPERIAL = 8

    DESCRIPTIONS = {
        NONE: "None",
        LEADERSHIP: "Leadership",
        DIPLOMACY: "Diplomacy",
        POLITICS: "Politics",
        CONSTRUCTION: "Construction",
        TRADE: "Trade",
        WARFARE: "Warfare",
        TECHNOLOGY: "Technology",
        IMPERIAL: "Imperial",
    }

    # use a list to keep the order
    ALL = [
        LEADERSHIP,
        DIPLOMACY,
        POLITICS,
        CONSTRUCTION,
        TRADE,
        WARFARE,
        TECHNOLOGY,
        IMPERIAL,
    ]

    @staticmethod
    def to_string(strategy: int):
        return Strategies.DESCRIPTIONS[strategy]

    @staticmethod
    def to_short_string(strategy: int):
        if 0 == strategy:
            return ""
        global USE_UNICODE
        if 1 <= strategy <= 8:
            if USE_UNICODE:
                if 1 == strategy:
                    return "\u2460"
                if 2 == strategy:
                    return "\u2461"
                if 3 == strategy:
                    return "\u2462"
                if 4 == strategy:
                    return "\u2463"
                if 5 == strategy:
                    return "\u2464"
                if 6 == strategy:
                    return "\u2465"
                if 7 == strategy:
                    return "\u2466"
                if 8 == strategy:
                    return "\u2467"
            else:
                return str(strategy)
        raise Exception(f"Invalid value for a strategy: {strategy}")

    @staticmethod
    def to_colour(strategy: int):
        if Strategies.NONE == strategy:
            return None
        return colours.STRATEGY_COLOURS[strategy - 1]


class Transition:
    def __init__(self, old, new=None):
        self._old = old
        self._new = new

    @property
    def changed(self):
        return self._old != self._new and self._new != None


class MetaTransition:
    def __init__(self):
        self.player = None
        self.phase = None
        self.turn = None
        self.round = None

    @property
    def empty(self):
        return (
            self.player is None
            or not self.player.changed
            and self.phase is None
            or not self.phase.changed
            and self.turn is None
            or not self.turn.changed
            and self.round is None
            or not self.round.changed
        )


class Game:
    # create the players with their colours
    STATE_INIT = 0
    STATE_PLAY = 1
    PHASE_STRATEGY = 1
    PHASE_ACTION = 2
    PHASE_STATUS = 3
    PHASE_AGENDA = 4

    def __init__(
        self,
        num_players: int = 6,
        speaker: int = 0,
        current_player: int = 0,
        state: int = STATE_INIT,
        turn: int = 1,
        round: int = 1,
        phase: int = PHASE_STRATEGY,
        available_strategies=None,
        players=None,
        available_colours=None,
    ):
        self._num_players = num_players
        self._speaker = speaker
        self._current_player = current_player
        self._state = state
        self._turn = turn
        self._round = round
        self._phase = phase
        self._iteration = 0  # count inside a turn
        if available_strategies:
            self._available_strategies = available_strategies
        else:
            self._available_strategies = {
                Strategies.LEADERSHIP: 0,
                Strategies.DIPLOMACY: 0,
                Strategies.POLITICS: 0,
                Strategies.CONSTRUCTION: 0,
                Strategies.TRADE: 0,
                Strategies.WARFARE: 0,
                Strategies.TECHNOLOGY: 0,
                Strategies.IMPERIAL: 0,
            }
        if players:
            self._players = players
        else:
            self._players = []
            for i in range(num_players):
                self._add_player()
        if available_colours:
            self._available_colours = available_colours
        else:
            self._available_colours = set(
                [
                    colours.PLAYER_BLACK,
                    colours.PLAYER_BLUE,
                    colours.PLAYER_GREEN,
                    colours.PLAYER_ORANGE,
                    colours.PLAYER_PINK,
                    colours.PLAYER_PURPLE,
                    colours.PLAYER_RED,
                    colours.PLAYER_YELLOW,
                ]
            )
        self._ordered_players = []

    def _add_player(self):
        num = len(self._players) + 1
        if num > 6:
            print("Too many players")
            return None
        player = Player(self, num, colours.PLAYER_BLANK)
        self._players.append(player)

    def get_player(self, num: int):
        if self._ordered_players:
            index = (num - 1) % len(self._ordered_players)
            return self._ordered_players[index]
        else:
            index = (num - 1) % self._num_players
            return self._players[index]

    # may not be a good idea
    @property
    def players(self):
        return self._players

    @property
    def num_players(self):
        return self._num_players

    def pick_colour(self, colour: Colour, former_colour=None):
        if colour not in self._available_colours:
            raise Exception(f"Colour {colour}, not available")
        self._available_colours.remove(colour)
        if former_colour:
            self._available_colours.add(former_colour)

    @property
    def players_ready_to_play(self):
        ready = not any([colours.PLAYER_BLANK == p.colour for p in self._players])
        return ready

    @property
    def players_have_strategy(self):
        ready = not any([Strategies.NONE == p.strategy for p in self._players])
        return ready

    @property
    def phase(self):
        return self._phase

    @property
    def round(self):
        return self._round

    def _next_round(self):
        self._turn += 1

    @property
    def turn(self):
        return self._turn

    def _next_turn(self):
        self._turn += 1

    @property
    def iteration(self):
        return self._iteration

    def _compute_time_key(self, round, turn, iteration):
        return round * 1000 + turn * 10 + iteration

    @property
    def time_key(self):
        return self._compute_time_key(self._round, self._turn, self._iteration)

    def get_time_key(self, iteration, turn=0, round=0):
        must_be_explicit = False
        if round == 0:
            round = self._round
        elif round != self._round:
            must_be_explicit = True
            if round < 0:
                round = self._round - round
                if round <= 0:
                    raise Exception(f"Computed invalid value for round: {round}")
        if turn == 0:
            if must_be_explicit:
                raise Exception("Turn must be explicit")
            else:
                turn = self._turn
        elif turn != self._turn:
            must_be_explicit = True
            if turn < 0:
                if must_be_explicit:
                    raise Exception("Turn must be explicit")
                else:
                    turn = self._turn - turn
                    if turn <= 0:
                        raise Exception(f"Computed invalid value for turn: {turn}")
        if iteration == 0:
            if must_be_explicit:
                raise Exception("iteration must be explicit")
            else:
                iteration = self._iteration
        elif iteration != self._iteration:
            if iteration < 0:
                if must_be_explicit:
                    raise Exception("iteration must be explicit")
                else:
                    iteration = self._iteration - iteration
                    if iteration <= 0:
                        raise Exception(
                            f"Computed invalid value for iteration: {iteration}"
                        )
        return self._compute_time_key(round, turn, iteration)

    def switch_state(self, new_state):
        self._state = new_state

    def start_playing(self):
        assert self.players_ready_to_play
        if Game.STATE_INIT == self._state:
            self.switch_state(Game.STATE_PLAY)
            self._turn = 0
            self._round = 1
            self._start_phase_strategy()
        else:
            raise Exception("It is not possible to start playing while already playing")

    def stop_playing(self):
        self.switch_state(Game.STATE_INIT)

    @property
    def state(self):
        return self._state

    @property
    def available_strategies(self):
        return self._available_strategies

    def _start_phase_strategy(self):
        self._ordered_players = []
        self._turn += 1
        self._phase = Game.PHASE_STRATEGY
        for strategy in set(Strategies.ALL) - set(self._available_strategies.keys()):
            self._available_strategies[strategy] = 0

    def _end_phase_strategy(self):
        for strategy in self._available_strategies.keys():
            self._available_strategies[strategy] += 1
        self._ordered_players = self.order_players()
        self._iteration = 0

    def _end_phase_action(self):
        raise Exception("Cannot only get next player in play state")

    def _end_phase_status(self):
        raise Exception("Cannot only get next player in play state")

    def _end_phase_agenda(self):
        raise Exception("Cannot only get next player in play state")

    def order_players(self):
        return sorted(self._players, key=lambda x: x.strategy * 10 + x.num)

    def set_speaker(self, num_player):
        self._speaker = num_player

    def is_speaker(self, num_player):
        return self._speaker == num_player

    def next(self):
        if Game.PHASE_STRATEGY == self._phase:
            if self.players_have_strategy:
                self._end_phase_strategy()
                self._phase = Game.PHASE_ACTION
        return self._phase

    def next_phase(self):
        if Game.STATE_PLAY != self._state:
            raise Exception("Can only go to next phase in play state")
        if Game.PHASE_STRATEGY == self._phase:
            self._end_phase_strategy()
            self._phase = Game.PHASE_ACTION
        elif Game.PHASE_ACTION == self._phase:
            self._end_phase_action()
            self._phase = Game.PHASE_AGENDA
        elif Game.PHASE_AGENDA == self._phase:
            self._end_phase_agenda()
            self._phase = Game.PHASE_STATUS
        elif Game.PHASE_STATUS == self._phase:
            self._end_phase_status()
            self._phase = Game.PHASE_STRATEGY
            self._next_round()

    def get_next_player(self) -> "Player":
        if Game.STATE_PLAY != self._state:
            raise Exception("Cannot only get next player in play state")
        if Game.PHASE_STRATEGY == self._phase:
            player = None
            if 0 == self._speaker:
                raise Exception("Missing speaker")
            if 0 == self._current_player:
                self._current_player = self._speaker
                player = self.get_player(self._current_player)
            else:
                for delta in range(self._num_players):
                    new_num = (self._current_player + delta) % 6 + 1
                    player = self.get_player(new_num)
                    if player.can_play:
                        self._current_player = new_num
                        break
            if player is None:
                raise Exception("Bug: no player found in get_next_player")
            return player
        elif Game.PHASE_ACTION == self._phase:
            raise Exception("Not implemented yet!")

    @property
    def current_player(self):
        if self._ordered_players:
            return self._ordered_players[self._current_player - 1]
        else:
            return self._players[self._current_player - 1]

    def __repr__(self):
        string = f"Game(num_players={self._num_players}, speaker={self._speaker}, "
        string += f"current_player={self._current_player}, state={self._state}, "
        string += f"turn={self._turn}, round={self._round}, phase={self._phase}, "
        string += f"available_strategies={self._available_strategies}, "
        string += f"players={self._players}, "
        string += f"available_colours={self._available_colours})"
        return string

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def build_fake_game(do_print=False):
        game = Game()
        if do_print:
            print(repr(game))

        player = game.get_player(5)
        player.name = "FLORENT"
        player.colour = colours.PLAYER_RED

        player = game.get_player(2)
        player.name = "PIERRE"
        try:
            player.colour = colours.PLAYER_RED
        except Exception as e:
            print("Red already taken:", e)
        player.colour = colours.PLAYER_BLACK

        player = game.get_player(4)
        player.name = "SHIZU"
        player.colour = colours.PLAYER_GREEN

        player = game.get_player(6)
        player.name = "JULIE"
        player.colour = colours.PLAYER_ORANGE

        player = game.get_player(1)
        player.name = "MICHAEL"
        player.colour = colours.PLAYER_PURPLE

        player = game.get_player(3)
        player.name = "ROMAIN"
        player.colour = colours.PLAYER_BLUE

        game.set_speaker(3)
        return game


class Property:
    def __init__(self, filename, default, name=None, value=None, game=None):
        self._config_prefix = "titable/"
        self._filename = filename
        self._default = default
        self._name = name if name else filename
        self._saved_value = default
        self._value = value
        self._game = game
        self._last_round = None

        path = self._get_path()
        if device.file_exists_and_not_empty(path):
            try:
                value = open(path, "r").read()
                self._value = self._cast(value)
                self._saved_value = self._value
                # print(f"Read {name}:", value)
            except Exception as ex:
                print(ex)
                print(f"Invalid file {self._name}, ignore")
        else:
            print(f"File does not exist: {path}")

    def _get_path(self):
        path = self._config_prefix
        if self._game is not None:
            self._last_round = self._game.round
            path += str(self._game.round) + "/"
        path += self._filename
        return path

    def _cast(self, value):
        return value

    @property
    def value(self):
        if self._value is None:
            return self._default
        else:
            return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def set(self, value):
        if self._value != value:
            self._value = value
            return True
        else:
            return False

    def write(self):
        if self._game:
            round_changed = self._last_round != self._game.round
        else:
            round_changed = False
        path = self._get_path()
        if self._value != self._saved_value or round_changed:
            if self._value == self._default or self._value == None:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"erase {path}")
                else:
                    print(f"write {path} SKIPPED (empty)")
            else:
                print(f"write {path}: {self._value}")
                open(path, "w").write(str(self._value))
            self._saved_value = self._value
        else:
            print(f"write {path} SKIPPED (unchanged)")

    def notify(self, key, value):
        # it is not very nice to have a specific case...
        if key == "colour":
            colour = value
            self._value = colour.id
        else:
            self._value = value


class PropertyInt(Property):
    def _cast(self, value):
        return int(value)


class PropertyBool(Property):
    def _cast(self, value):
        return bool(value)


class Player:
    # FACTION_NOT_IMPLEMENTED = 0
    def __init__(
        self,
        game: Game,
        num: int,
        # faction:int = FACTION_NOT_IMPLEMENTED,
        # score: int = 0,  NOT IMPLEMENTED YET
        has_passed=None,  # bool
        has_played_strategy=None,  # bool
        strategy=None,  # int
    ):
        self._game = game
        self._num = num
        self._name = Property(f"player_{num}_name", f"Player {num}", f"player ({num})")
        self._saved_colour = PropertyInt(
            f"player_{num}_colour", colours.PLAYER_BLANK.id, f"colour ({num})"
        )
        if colours.PLAYER_BLANK.id == self._saved_colour.value:
            self._colour = colours.PLAYER_BLANK
        else:
            self._colour = colours.PLAYER_COLOURS[self._saved_colour.value]
        # self._score = PropertyInt(f"player_{num}_score", 0, f"score ({num})", score)
        self._has_passed = PropertyBool(
            f"player_{num}_has_passed", False, f"has passed ({num})", has_passed, game
        )
        self._has_played_strategy = PropertyBool(
            f"player_{num}_has_played_strategy",
            False,
            f"has played strategy ({num})",
            has_played_strategy,
            game,
        )
        self._strategy = PropertyInt(
            f"player_{num}_strategy",
            Strategies.NONE,
            f"strategy ({num})",
            strategy,
            game,
        )
        self._observers_name = []
        self._observers_colour = [self._saved_colour]

    def add_observer_name(self, observer):
        if observer not in self._observers_name:
            self._observers_name.append(observer)

    def add_observer_colour(self, observer):
        if observer not in self._observers_colour:
            self._observers_colour.append(observer)

    def remove_observer_name(self, observer):
        self._observers_name.remove(observer)

    def remove_observer_colour(self, observer):
        self._observers_colour.remove(observer)

    # @property
    # def score(self):
    #     return self._score

    # def add_score(self, delta: int):
    #     self._score += delta

    @property
    def name(self):
        return self._name.value

    @name.setter
    def name(self, name):
        if self._name.set(name):
            if self._observers_name:
                for observer in self._observers_name:
                    observer.notify("name", name)

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, colour):
        if self._colour != colour:
            self._game.pick_colour(colour, self._colour)
            self._colour = colour
            if self._observers_colour:
                for observer in self._observers_colour:
                    observer.notify("colour", colour)

    @property
    def num(self):
        return self._num

    @property
    def can_play(self):
        phase = self._game.phase
        if Game.PHASE_STRATEGY == phase:
            return self._strategy.value == Strategies.NONE
        elif Game.PHASE_ACTION == phase:
            return not self._has_passed.value
        else:
            # this might be more complex, but we don't really know
            # maybe it makes no sense to call this for other phases now.
            return True

    @property
    def can_pass(self):
        phase = self._game.phase
        if Game.PHASE_ACTION != phase:
            return False
        return self._has_played_strategy.value

    @property
    def has_passed(self):
        return self._has_passed.value

    def do_pass(self):
        self._has_passed = True

    def set_speaker(self):
        self._game.set_speaker(self._num)

    def is_speaker(self):
        return self._game.is_speaker(self.num)

    @property
    def strategy(self):
        return self._strategy.value

    @strategy.setter
    def strategy(self, strategy: int):
        self._strategy.value = strategy
        self._has_played_strategy.value = False

    @property
    def has_played_strategy(self):
        return self._has_played_strategy.value

    def use_strategy(self):
        self._has_played_strategy.value = True

    @property
    def previous(self):
        return self._game.get_player(self.num - 1)

    @property
    def next(self):
        return self._game.get_player(self.num + 1)

    def __repr__(self):
        string = f"Player(num={self._num}, name={self._name.value}, "
        string += f"colour={self._colour}, has_passed={self._has_passed.value}, "
        string += f"has_played_strategy={self._has_played_strategy.value}, "
        string += f"strategy={self._strategy.value})"
        return string

    def __str__(self):
        return self.__repr__()

    def write_name(self):
        self._name.write()

    def write_colour(self):
        self._saved_colour.write()

    def write_strategy(self):
        self._strategy.write()

    def write_others(self):
        self._has_played_strategy.write()
        self._has_passed.write()

    def write(self):
        self.write_name()
        self.write_colour()
        self.write_strategy()
        self.write_others()


def main():
    game = Game.build_fake_game(do_print=True)

    for player in game._players:
        print(player)

    game.start_playing()
    player = game.get_next_player()
    player.strategy = Strategies.WARFARE
    player = game.get_next_player()
    player.strategy = Strategies.TECHNOLOGY
    player = game.get_next_player()
    player.strategy = Strategies.TRADE
    player = game.get_next_player()
    player.strategy = Strategies.LEADERSHIP
    player = game.get_next_player()
    player.strategy = Strategies.CONSTRUCTION
    player = game.get_next_player()
    player.strategy = Strategies.POLITICS

    print(repr(game))

    game.next_phase()

    for player in game._ordered_players:
        print(player)
    pass


if "__main__" == __name__:
    main()
