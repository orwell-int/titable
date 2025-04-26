ALL = 0
RETURN = 1
SETUP = 2
PLAY = 3
RESET = 4
SETUP_COLOUR = 6
PICK_COLOUR = 7
SWAP = 8
STRATEGY_PLAYER = 9
PICK_STRATEGY = 10
PICK_STRATEGY_SWAP = 11
UNPICK_STRATEGY_SWAP = 12
SWAP_STRATEGY = 13
SETUP_NAME = 20
NEXT = 30
PREVIOUS = 31
PLAY_STRATEGY = 32
PLAY_TACTICAL_OR_COMPONENT = 33
PLAY_SKIP = 34
PLAY_PASS = 35
RESET_PHASE = 48
RESET_ROUND = 49
WELCOME = 99

ALL_EVENTS = [
    RETURN,
    SETUP,
    PLAY,
    RESET,
    SETUP_COLOUR,
    PICK_COLOUR,
    SWAP,
    STRATEGY_PLAYER,
    PICK_STRATEGY,
    PICK_STRATEGY_SWAP,
    UNPICK_STRATEGY_SWAP,
    SWAP_STRATEGY,
    SETUP_NAME,
    NEXT,
    PREVIOUS,
    PLAY_STRATEGY,
    PLAY_TACTICAL_OR_COMPONENT,
    PLAY_SKIP,
    PLAY_PASS,
    RESET_PHASE,
    RESET_ROUND,
    WELCOME,
]


class EventsHanlder:
    def __init__(self):
        super().__init__()
        self._registered = {}
        self._registered_once = {}

    def register(self, event: int, item):
        # print(f"register(event={event}, item={item}")
        if ALL == event:
            for event in ALL_EVENTS:
                self.register(event, item)
        if event not in self._registered:
            self._registered[event] = [item]
        else:
            self._registered[event].append(item)

    def register_once(self, event: int, item):
        if event not in self._registered_once:
            self._registered_once[event] = [item]
        else:
            self._registered_once[event].append(item)

    def unregister(self, event: int, item):
        if ALL == event:
            for event in ALL_EVENTS:
                self.unregister(event, item)
        if event in self._registered:
            if item in self._registered[event]:
                self._registered[event].remove(item)
        if event in self._registered_once:
            if item in self._registered_once[event]:
                self._registered_once[event].remove(item)

    def send_event(self, sender, event: int, args=None):
        #print(f"send_event event {to_string(event)} args {args}")
        if event in self._registered:
            for item in self._registered[event]:
                item.do_event(sender, event, args)
        if event in self._registered_once:
            for item in self._registered_once[event]:
                item.do_event(sender, event, args)
            del self._registered_once[event]


HANDLER = EventsHanlder()


def to_string(event: int):
    if ALL == event:
        return "ALL"
    elif RETURN == event:
        return "RETURN"
    elif SETUP == event:
        return "SETUP"
    elif PLAY == event:
        return "PLAY"
    elif RESET == event:
        return "RESET"
    elif SETUP_COLOUR == event:
        return "SETUP_COLOUR"
    elif PICK_COLOUR == event:
        return "PICK_COLOUR"
    elif SWAP == event:
        return "SWAP"
    elif STRATEGY_PLAYER == event:
        return "STRATEGY_PLAYER"
    elif PICK_STRATEGY == event:
        return "PICK_STRATEGY"
    elif PICK_STRATEGY_SWAP == event:
        return "PICK_STRATEGY_SWAP"
    elif UNPICK_STRATEGY_SWAP == event:
        return "UNPICK_STRATEGY_SWAP"
    elif SWAP_STRATEGY == event:
        return "SWAP_STRATEGY"
    elif SETUP_NAME == event:
        return "SETUP_NAME"
    elif NEXT == event:
        return "NEXT"
    elif PREVIOUS == event:
        return "PREVIOUS"
    elif PLAY_STRATEGY == event:
        return "PLAY_STRATEGY"
    elif PLAY_TACTICAL_OR_COMPONENT == event:
        return "PLAY_TACTICAL_OR_COMPONENT"
    elif PLAY_SKIP == event:
        return "PLAY_SKIP"
    elif PLAY_PASS == event:
        return "PLAY_PASS"
    elif RESET_PHASE == event:
        return "RESET_PHASE"
    elif RESET_ROUND == event:
        return "RESET_ROUND"
    elif WELCOME == event:
        return "WELCOME"
    else:
        return "OOPS"
