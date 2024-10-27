import colours
from colours import Colour


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

    ALL = set(
        [
            LEADERSHIP,
            DIPLOMACY,
            POLITICS,
            CONSTRUCTION,
            TRADE,
            WARFARE,
            TECHNOLOGY,
            IMPERIAL,
        ]
    )

    @staticmethod
    def to_string(strategy: int):
        return Strategies[strategy]


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
        turn: int = 0,
        round: int = 0,
        phase: int = PHASE_STRATEGY,
        available_strategies: dict = None,
        players: dict = None,
        available_colours: set[Colour] = None,
    ):
        self._num_players = num_players
        self._speaker = speaker
        self._current_player = current_player
        self._state = state
        self._turn = turn
        self._round = round
        self._phase = phase
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
                    colours.BLACK,
                    colours.BLUE,
                    colours.GREEN,
                    colours.ORANGE,
                    colours.PINK,
                    colours.PURPLE,
                    colours.RED,
                    colours.YELLOW,
                ]
            )
        self._ordered_players = None

    def _add_player(self):
        num = len(self._players) + 1
        if num > 6:
            print("Too many players")
            return None
        player = Player(num, f"Player {num}", colours.BLANK)
        player.set_game(self)
        self._players.append(player)

    def get_player(self, num: int):
        try:
            return self._players[num - 1]
        except IndexError:
            return None

    @property
    def num_players(self):
        return self._num_players

    def pick_colour(self, colour):
        if colour not in self._available_colours:
            raise Exception(f"Colour {colour}, not available")
        self._available_colours.remove(colour)

    @property
    def phase(self):
        return self._phase

    def switch_state(self, new_state):
        self._state = new_state

    def start_playing(self):
        self.switch_state(Game.STATE_PLAY)
        self._turn = 0
        self._round = 1
        self._start_phase_strategy()

    def _start_phase_strategy(self):
        self._turn += 1
        self._phase = Game.PHASE_STRATEGY
        for strategy in Strategies.ALL - self._available_strategies.keys():
            self._available_strategies[strategy] = 0

    def _end_phase_strategy(self):
        for strategy in self._available_strategies.keys():
            self._available_strategies[strategy] += 1
        self._order_players()

    def _order_players(self):
        self._ordered_players = sorted(self._players, key=lambda x: x._strategy)

    def set_speaker(self, num_player):
        self._speaker = num_player

    def is_speaker(self, num_player):
        return self._speaker == num_player

    def next_phase(self):
        if Game.STATE_PLAY != self._state:
            raise Exception("Cannot only only go to next phase in play state")
        if Game.PHASE_STRATEGY == self._phase:
            self._end_phase_strategy()
            self._phase = Game.PHASE_ACTION

    def get_next_player(self):
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
                    if player.can_play():
                        self._current_player = new_num
                        break
            return player
        elif Game.PHASE_ACTION == self._phase:
            raise Exception("Not implemented yet!")

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


class Player:
    # FACTION_NOT_IMPLEMENTED = 0
    def __init__(
        self,
        num: int,
        name: str,
        colour: Colour,
        # faction:int = FACTION_NOT_IMPLEMENTED,
        score: int = 0,
        has_passed: bool = False,
        has_played_strategy: bool = False,
        strategy: int = Strategies.NONE,
    ):
        self._game = None
        self._num = num
        self._name = name
        self._colour = colour
        self._score = score
        self._has_passed = has_passed
        self._has_played_strategy = has_played_strategy
        self._strategy = strategy

    def set_game(self, game):
        self._game = game

    @property
    def score(self):
        return self._score

    def add_score(self, delta: int):
        self._score += delta

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, colour):
        self._game.pick_colour(colour)
        self._colour = colour

    def can_play(self):
        phase = self._game.phase
        if Game.PHASE_STRATEGY == phase:
            return self._strategy == Strategies.NONE
        elif Game.PHASE_ACTION == phase:
            return not self._has_passed
        else:
            # this might be more complex, but we don't really know
            # maybe it makes no sense to call this for other phases now.
            return True

    def set_speaker(self):
        self.game.set_speaker(self._num)

    def is_speaker(self):
        return self._game.is_speaker(self.num)

    def set_strategy(self, strategy: int):
        self._strategy = strategy
        self._has_played_strategy = False

    def use_strategy(self):
        self._has_played_strategy = True

    def __repr__(self):
        string = f"Player(num={self._num}, name={self._name}, "
        string += f"colour={self._colour}, has_passed={self._has_passed}, "
        string += f"has_played_strategy={self._has_played_strategy}, "
        string += f"strategy={self._strategy})"
        return string

    def __str__(self):
        return self.__repr__()


def main():
    game = Game()
    print(repr(game))

    player = game.get_player(5)
    player.name = "Florent"
    player.colour = colours.RED

    player = game.get_player(2)
    player.name = "Pierre"
    try:
        player.colour = colours.RED
    except Exception as e:
        print("Red already taken:", e)
    player.colour = colours.BLACK

    player = game.get_player(4)
    player.name = "Shizu"
    player.colour = colours.GREEN

    player = game.get_player(6)
    player.name = "Julie"
    player.colour = colours.ORANGE

    player = game.get_player(1)
    player.name = "Michael"
    player.colour = colours.PURPLE

    player = game.get_player(3)
    player.name = "Romain"
    player.colour = colours.BLUE

    game.set_speaker(3)

    for player in game._players:
        print(player)

    game.start_playing()
    player = game.get_next_player()
    player.set_strategy(Strategies.WARFARE)
    player = game.get_next_player()
    player.set_strategy(Strategies.TECHNOLOGY)
    player = game.get_next_player()
    player.set_strategy(Strategies.TRADE)
    player = game.get_next_player()
    player.set_strategy(Strategies.LEADERSHIP)
    player = game.get_next_player()
    player.set_strategy(Strategies.CONSTRUCTION)
    player = game.get_next_player()
    player.set_strategy(Strategies.POLITICS)

    print(repr(game))

    game.next_phase()

    for player in game._ordered_players:
        print(player)
    pass


if "__main__" == __name__:
    main()
