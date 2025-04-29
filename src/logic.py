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
        phase: int = PHASE_STRATEGY,
        round: int = 1,
        turn: int = 1,
        available_strategies=None,
        players=None,
        available_colours=None,
        restore: bool = False,
    ):
        if restore:
            self.read()
            self._players = []
            self._available_colours = set(colours.PLAYER_COLOURS)
            for _ in range(self._num_players):
                player = self._add_player()
                if player.colour != colours.PLAYER_NEUTRAL:
                    if player.colour in self._available_colours:
                        self._available_colours.remove(player.colour)
            if self._phase > Game.PHASE_STRATEGY:
                self._ordered_players = self.order_players()
            return
        self._num_players = num_players
        self._speaker = speaker
        self._current_player = current_player
        self._previous_player = None
        self._next_player = None
        self._state = state
        self._phase = phase
        self._round = round
        self._turn = turn
        self._iteration = 0  # count inside a turn
        self._player_index_to_hide_next = None
        self._player_index_to_hide_now = None
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
            self._available_colours = set(colours.PLAYER_COLOURS)
        self._ordered_players = []

    def _to_str_uint(self, value):
        if value is None:
            return "-1"
        else:
            return str(value)

    def _from_str_uint(self, value):
        int_value = int(value)
        if int_value < 0:
            return None
        else:
            return int_value

    def _get_names(self):
        for item in (
            "_num_players",
            "_speaker",
            "_state",
            "_phase",
            "_round",
            "_turn",
            "_iteration",
        ):
            yield item

    def _get_unames(self):
        for uitem in (
            "_current_player",
            "_previous_player",
            "_next_player",
            "_player_index_to_hide_next",
            "_player_index_to_hide_now",
        ):
            yield uitem

    @property
    def _separator(self):
        return ", "

    def to_content(self):
        content = []
        for name in self._get_names():
            item = getattr(self, name)
            content.append(str(item))
        content.append("u")
        for uname in self._get_unames():
            uitem = getattr(self, uname)
            content.append(self._to_str_uint(uitem))
        content.append("s")
        for strategy in Strategies.ALL:
            goods = self._available_strategies[strategy]
            content.append(str(goods))

        return self._separator.join(content)

    def from_content(self, iter_content):
        iter_content = iter_content.split(self._separator).__iter__()
        for name, value in zip(self._get_names(), iter_content):
            setattr(self, name, int(value))
        u = next(iter_content)
        assert u == "u"
        for uname, value in zip(self._get_unames(), iter_content):
            setattr(self, uname, self._from_str_uint(value))
        s = next(iter_content)
        assert s == "s"
        self._available_strategies = {}
        for strategy, str_goods in zip(Strategies.ALL, iter_content):
            self._available_strategies[strategy] = int(str_goods)

    def _get_path(self):
        return f"titable/game"

    def write(self, also_write_players=False):
        open(self._get_path(), "w").write(self.to_content())
        if also_write_players:
            for player in self._players:
                player.write()

    def read(self):
        self.from_content(open(self._get_path(), "r").read())

    def _add_player(self):
        num = len(self._players) + 1
        if num > self._num_players:
            raise Exception("Too many players")
        player = Player(self, num)
        player.add_observer_passed(self)
        self._players.append(player)
        return player

    def get_player(self, num: int):
        index = (num - 1) % self._num_players
        if self._ordered_players:
            return self._ordered_players[index]
        else:
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
        if former_colour and former_colour != colours.PLAYER_BLANK:
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
    def players_have_passed(self):
        passed = all([p.has_passed for p in self._players])
        # print("players_have_passed ?", passed)
        return passed

    @property
    def phase(self):
        return self._phase

    @property
    def round(self):
        return self._round

    def _next_round(self):
        self._round += 1
        self._turn = 1
        for player in self._players:
            player.go_to_next_turn()
        self._start_phase_strategy()

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
        self._previous_player = None
        self._ordered_players = []
        self._phase = Game.PHASE_STRATEGY
        for strategy in set(Strategies.ALL) - set(self._available_strategies.keys()):
            self._available_strategies[strategy] = 0

    def _end_phase_strategy(self):
        for strategy in self._available_strategies.keys():
            self._available_strategies[strategy] += 1
        self._ordered_players = self.order_players()
        print("ordered players:")
        print(" - " + "\n - ".join([str(p) for p in self._ordered_players]))

    def _start_phase_action(self):
        self._phase = Game.PHASE_ACTION
        self._turn = 1
        self._iteration = 0
        self._current_player = 1
        self._next_player = 2
        self._previous_player = None
        self._active_players = self._num_players
        self._player_index_to_hide_now = None
        self._player_index_to_hide_next = None

    def _end_phase_action(self):
        print("_end_phase_action")
        self._phase = Game.PHASE_AGENDA
        self._iteration = 0
        self._ordered_players = []
        for player in self._players:
            player.unhide()
        self._turn = 0

    def _start_phase_status(self):
        self._iteration = 0
        self._current_player = 1
        self._next_player = 2
        self._previous_player = None

    def _end_phase_status(self):
        self._iteration = 0

    def _end_phase_agenda(self):
        pass

    def order_players(self):
        return sorted(self._players, key=lambda x: x.strategy * 10 + x.num)

    def set_speaker(self, num_player):
        self._speaker = num_player

    def is_speaker(self, num_player):
        return self._speaker == num_player

    def print_player_nums(self, text):
        p = self.previous_player.num if self.previous_player else "x"
        c = self.current_player.num if self.current_player else "x"
        n = self.next_player.num if self.next_player else "x"
        print(f"{text} p | c | n : {p} | {c} | {n}")

    def next(self):
        self.print_player_nums("next")
        if Game.PHASE_STRATEGY == self._phase:
            if self.players_have_strategy:
                self._end_phase_strategy()
                self._start_phase_action()
        elif Game.PHASE_ACTION == self._phase:
            if self.players_have_passed:
                self._end_phase_action()
            else:
                self._previous_player = self._current_player
                self._hide_player()
                self._current_player = self._next_player
                self._compute_next_player()
                print("ordered players:")
                print(" - " + "\n - ".join([str(p) for p in self._ordered_players]))
                self.print_player_nums("next ++action")
        elif Game.PHASE_AGENDA == self._phase:
            self._end_phase_agenda()
            # skip status phase for now
            skip_status_phase = True
            if skip_status_phase:
                self._start_phase_strategy()
                # self._phase = Game.PHASE_STRATEGY
                self._next_round()
            else:
                self._phase = Game.PHASE_STATUS
                self._start_phase_status()
        elif Game.PHASE_STATUS == self._phase:
            if self._next_player is None:
                self._end_phase_status()
                self._phase = Game.PHASE_STRATEGY
                self._next_round()
            else:
                self._previous_player = self._current_player
                self._current_player = self._next_player
                self._compute_next_player()
                self.print_player_nums("next ++status")
        return self._phase

    # def get_next_player(self) -> "Player":
    #     if Game.STATE_PLAY != self._state:
    #         raise Exception("Cannot only get next player in play state")
    #     if Game.PHASE_STRATEGY == self._phase:
    #         player = None
    #         if 0 == self._speaker:
    #             raise Exception("Missing speaker")
    #         if 0 == self._current_player:
    #             self._current_player = self._speaker
    #             player = self.get_player(self._current_player)
    #         else:
    #             for delta in range(self._num_players):
    #                 new_num = (self._current_player + delta) % 6 + 1
    #                 player = self.get_player(new_num)
    #                 if player.can_play:
    #                     self._current_player = new_num
    #                     break
    #         if player is None:
    #             raise Exception("Bug: no player found in get_next_player")
    #         return player
    #     elif Game.PHASE_ACTION == self._phase:
    #         raise Exception("Not implemented yet!")

    @property
    def current_player(self):
        if self._current_player is None:
            return None
        if self._ordered_players:
            return self._ordered_players[self._current_player - 1]
        else:
            return self._players[self._current_player - 1]

    @property
    def previous_player(self):
        if Game.PHASE_STRATEGY == self._phase:
            return None
        elif Game.PHASE_ACTION == self._phase:
            if self._previous_player is None:
                return None
            return self._ordered_players[self._previous_player - 1]
        elif Game.PHASE_AGENDA == self._phase:
            # not implemented...
            return None
        elif Game.PHASE_STATUS == self._phase:
            if self._previous_player is None:
                return None
            return self._players[self._previous_player - 1]
        else:
            return None

    def _hide_player(self):
        if self._player_index_to_hide_now is not None:
            player_index = self._player_index_to_hide_now
            self._player_index_to_hide_now = None
            self._ordered_players[player_index].hide()
        if self._player_index_to_hide_next is not None:
            self._player_index_to_hide_now = self._player_index_to_hide_next
            self._player_index_to_hide_next = None
        # print(f"Future hides: {self._player_index_to_hide_now} | {self._player_index_to_hide_next}")

    def _compute_next_player(self):
        # print(f"_compute_next_player R {self._round} T {self._turn} I {self._iteration}")
        if Game.PHASE_ACTION == self._phase:
            assert self._next_player is not None
            self._next_player = self._next_player + 1
            loop = True
            while loop:
                # print(f" % next player:", self._next_player)
                if self._next_player > self._num_players:
                    self._next_player = 1
                player = self._ordered_players[self._next_player - 1]
                if player.hidden:
                    # print(" skip hidden player")
                    self._next_player += 1
                else:
                    loop = False
            if self._iteration >= self._active_players - 1:
                print(" next turn")
                self._iteration = 0
                self._turn += 1
                self._active_players = 0
                for player in self._ordered_players:
                    if not player.hidden:
                        self._active_players += 1
            else:
                self._iteration += 1
        elif Game.PHASE_STATUS == self._phase:
            assert self._next_player is not None
            self._next_player = self._next_player + 1
            if self._next_player > self._num_players:
                self._next_player = 1
            self._iteration += 1
            if self._iteration == self._num_players - 1:
                self._next_player = None

    @property
    def next_player(self):
        if Game.PHASE_ACTION == self._phase:
            if self._next_player is None:
                return None
            return self._ordered_players[self._next_player - 1]
        elif Game.PHASE_STATUS == self._phase:
            if self._next_player is None:
                return None
            return self._players[self._next_player - 1]
        return None
        # raise Exception(f"next_player -> not implemented for phase {self._phase}")

    def notify(self, key, value):
        if key == "passed":
            passing_player = value
            print(f"Remove from active players: {passing_player}")
            remove_index = None
            for index, player in enumerate(self._ordered_players):
                if player == passing_player:
                    remove_index = index
                    break
            if remove_index is None:
                raise Exception(f"Unable to remove passing player: {passing_player}")
            else:
                self._player_index_to_hide_next = remove_index

    def __repr__(self):
        string = f"Game(num_players={self._num_players}, speaker={self._speaker}, "
        string += f"current_player={self._current_player}, "
        string += f"previous_player={self._previous_player}, "
        string += f"next_player={self._next_player}, "
        string += f"player_index_to_hide_next={self._player_index_to_hide_next}, "
        string += f"player_index_to_hide_now={self._player_index_to_hide_now}, "
        string += f"state={self._state}, "
        string += f"phase={self._phase}, round={self._round}, turn={self._turn}, "
        string += f"iteration={self._iteration}, "
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

        self.read()

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

    def read(self):
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
        if key == "colour":
            # it is not very nice to have a specific case...
            colour = value
            self._value = colour.id
        else:
            self._value = value

    def reset(self):
        self._value = self._default
        self._saved_value = self._default


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
        hidden=None,  # bool
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
        self._hidden = PropertyBool(
            f"player_{num}_hidden",
            False,
            f"hidden ({num})",
            hidden,
            game,
        )
        self._observers_name = []
        self._observers_colour = [self._saved_colour]
        self._observers_passed = []

    def add_observer_name(self, observer):
        if observer not in self._observers_name:
            self._observers_name.append(observer)

    def add_observer_colour(self, observer):
        if observer not in self._observers_colour:
            self._observers_colour.append(observer)

    def add_observer_passed(self, observer):
        if observer not in self._observers_passed:
            self._observers_passed.append(observer)

    def remove_observer_name(self, observer):
        self._observers_name.remove(observer)

    def remove_observer_colour(self, observer):
        self._observers_colour.remove(observer)

    def remove_observer_passed(self, observer):
        self._observers_passed.remove(observer)

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
        self._has_passed.value = True
        if self._observers_passed:
            for observer in self._observers_passed:
                observer.notify("passed", self)

    def set_speaker(self):
        self._game.set_speaker(self._num)

    def is_speaker(self):
        return self._game.is_speaker(self._num)

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
    def hidden(self):
        return self._hidden.value

    def hide(self):
        print("Hide player", self._num)
        self._hidden.value = True

    def unhide(self):
        self._hidden.value = False

    # @property
    # def previous(self):
    #     for delta in range(1, self._game.num_players):
    #         player = self._game.get_player(self.num - delta)
    #         if not player.hidden:
    #             return player
    #     return self

    # @property
    # def next(self):
    #     for delta in range(1, self._game.num_players):
    #         player = self._game.get_player(self.num + delta)
    #         if not (player.hidden or player.has_passed):
    #             return player
    #     return self

    def __repr__(self):
        string = f"Player(num={self._num}, name={self._name.value}, "
        string += f"colour={self._colour}, has_passed={self._has_passed.value}, "
        string += f"has_played_strategy={self._has_played_strategy.value}, "
        string += f"hidden={self._hidden.value}, "
        string += f"strategy={self._strategy.value})"
        return string

    def __str__(self):
        return self.__repr__()

    def read_name(self):
        self._name.read()

    def read_colour(self):
        self._saved_colour.read()

    def read_strategy(self):
        self._strategy.read()

    def read_others(self):
        self._has_played_strategy.read()
        self._has_passed.read()
        self._hidden.read()

    def read(self):
        self.read_name()
        self.read_colour()
        self.read_strategy()
        self.read_others()

    def write_name(self):
        self._name.write()

    def write_colour(self):
        self._saved_colour.write()

    def write_strategy(self):
        self._strategy.write()

    def write_others(self):
        # those are put together because they can change implicitly
        self._has_played_strategy.write()
        self._has_passed.write()
        self._hidden.write()

    def write(self):
        self.write_name()
        self.write_colour()
        self.write_strategy()
        self.write_others()

    def go_to_next_turn(self):
        self._strategy.reset()
        self._has_played_strategy.reset()
        self._has_passed.reset()
        self._hidden.reset()


def main():
    # not compatible with device!
    import sys
    import file_mock

    select = 1
    if len(sys.argv) > 1:
        try:
            param = int(sys.argv[1])
            if 0 < param <= 2:
                select = param
        except:
            pass

    if 1 == select:
        game = Game.build_fake_game(do_print=True)

        for player in game._players:
            print(player)

        game.start_playing()
        game.next()
        player = game.current_player
        player.strategy = Strategies.WARFARE
        game.next()
        player = game.current_player
        player.strategy = Strategies.TECHNOLOGY
        game.next()
        player = game.current_player
        player.strategy = Strategies.TRADE
        game.next()
        player = game.current_player
        player.strategy = Strategies.LEADERSHIP
        game.next()
        player = game.current_player
        player.strategy = Strategies.CONSTRUCTION
        game.next()
        player = game.current_player
        player.strategy = Strategies.POLITICS

        print(repr(game))

        game._end_phase_strategy()

        for player in game._ordered_players:
            print(player)
    elif 2 == select:
        with file_mock.do():
            game = Game.build_fake_game(do_print=True)
            print(repr(game))
            print("** Write **")
            game.write(also_write_players=True)

            print(repr(game))
            print("** Restore **")
            other_game = Game(restore=True)

            print(repr(game))
            print(repr(other_game))


if "__main__" == __name__:
    main()
