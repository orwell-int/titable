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
SETUP_NAME = 14
NEXT = 23
PREVIOUS = 24
PLAY_STRATEGY = 25
PLAY_TACTICAL_OR_COMPONENT = 26
PLAY_SKIP = 27
PLAY_PASS = 28
RESET_PHASE = 41
RESET_ROUND = 42
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

    def send_event(self, event: int, args=None):
        if event in self._registered:
            for item in self._registered[event]:
                item.do_event(event, args)
        if event in self._registered_once:
            for item in self._registered_once[event]:
                item.do_event(event, args)
            del self._registered_once[event]


HANDLER = EventsHanlder()
