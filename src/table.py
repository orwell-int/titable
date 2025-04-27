import time

import logic
import screens
from screens import ScreenTypes
import events
import leds
import device

import M5


class Titable:
    def __init__(self, leds_only_print=False):
        self._game = logic.Game()
        self._screens = {}
        self._current_screen_type = ScreenTypes.WELCOME
        self._current_screen = None
        self._saved_screen = None
        self._lights = leds.Lights(only_print=leds_only_print)
        self.switch_to_screen_welcome()
        events.HANDLER.register(events.ALL, self)
        self._touched = False

    def do_event(self, sender, event: int, args):
        if events.RETURN == event:
            self.switch_to_previous_screen()
        elif events.SETUP == event:
            self.switch_to_screen_setup()
        elif events.PLAY == event:
            self.resume_play()
        elif events.RESET == event:
            pass
        elif events.SETUP_COLOUR == event:
            player = args["player"]
            self.switch_to_screen_setup_colour(player)
        elif events.PICK_COLOUR == event:
            colour = args["colour"]
            player = args["player"]
            # print(f"Set player ({player.name}) colour to {colour}")
            player.colour = colour
        elif events.SWAP == event:
            pass
        elif events.STRATEGY_PLAYER == event:
            player = args["player"]
            self.switch_to_screen_startegy_player(player)
        elif events.PICK_STRATEGY == event:
            pass
        elif events.SETUP_NAME == event:
            pass
        elif events.NEXT == event:
            pass
        elif events.PREVIOUS == event:
            pass
        elif events.PLAY_STRATEGY == event:
            pass
        elif events.PLAY_TACTICAL_OR_COMPONENT == event:
            pass
        elif events.PLAY_SKIP == event:
            pass
        elif events.PLAY_PASS == event:
            pass
        elif events.RESET_PHASE == event:
            pass
        elif events.RESET_ROUND == event:
            pass
        elif events.WELCOME == event:
            pass

    def touch(self, x: int, y: int):
        if (x is None) or (y is None):
            self._touched = False
            return
        # print(f"table touch {x} {y} touched ? {self._touched}")
        if self._touched:
            return
        self._touched = True
        assert self._current_screen is not None
        self._current_screen.touch(x, y)

    def switch_to_screen_welcome(self):
        print("switch_to_screen_welcome")
        if self._current_screen:
            self._current_screen.hide()
            self._game.stop_playing()
        self._current_screen = screens.ScreenWelcome(self._lights, self._game)
        self._current_screen.draw()

    def resume_play(self):
        self._game.start_playing()
        phase = self._game.phase
        if logic.Game.PHASE_STRATEGY == phase:
            self.switch_to_screen_startegy()
        else:
            raise Exception(f"Not implemented yet (resume_play from phase {phase} )")

    def switch_to_screen_startegy(self):
        print("switch_to_screen_strategy")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenStrategy(self._lights, self._game)
        self._current_screen.draw()

    def switch_to_screen_startegy_player(self, player):
        print("switch_to_screen_strategy_player")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenStrategyPlayer(
            self._lights, self._game, player.num
        )
        self._current_screen.draw()

    def switch_to_previous_screen(self, return_screen=None):
        assert self._current_screen is not None
        if return_screen is None:
            return_screen = self._current_screen.on_return
        if ScreenTypes.WELCOME == return_screen:
            self.switch_to_screen_welcome()
        elif ScreenTypes.SETUP_PLAYERS == return_screen:
            self.switch_to_screen_setup()
        elif ScreenTypes.SETUP_PLAYER_NAME == return_screen:
            raise Exception("It is not possible to switch back to SETUP_PLAYER_NAME")
        elif ScreenTypes.SETUP_PLAYER_COLOUR == return_screen:
            raise Exception("It is not possible to switch back to SETUP_PLAYER_COLOUR")
        elif ScreenTypes.STRATEGY_MAIN == return_screen:
            self.switch_to_screen_startegy()
        elif ScreenTypes.STRATEGY_PLAYER == return_screen:
            raise Exception("It is not possible to switch back to STRATEGY_PLAYER")
        elif ScreenTypes.ACTION_PLAYER == return_screen:
            pass
        elif ScreenTypes.STATUS_PLAYER == return_screen:
            pass
        elif ScreenTypes.MENU == return_screen:
            pass
        elif ScreenTypes.SAVED_SCREEN == return_screen:
            pass

    def switch_to_screen_setup(self):
        print("switch_to_screen_setup")
        assert self._current_screen is not None
        self._current_screen.hide()
        self._current_screen = screens.ScreenSetup(self._lights, self._game.players)
        self._current_screen.draw()

    def switch_to_screen_setup_colour(self, player: logic.Player):
        print("switch_to_screen_setup_colour")
        assert self._current_screen is not None
        self._current_screen.hide()
        self._current_screen = screens.ScreenSetupColour(
            self._lights, self._game.players, player
        )
        self._current_screen.draw()


def inner_main():
    titable = Titable(leds_only_print=True)
    if not device.is_micropython():
        M5.TITABLE = titable
    auto_touch = False
    if auto_touch:
        if not device.is_micropython():
            M5.update()
            time.sleep(2)
        titable._current_screen._button_setup.force_touch()
        if not device.is_micropython():
            M5.update()
            time.sleep(2)
        titable._current_screen._button_return.force_touch()
    if not device.is_micropython():
        while True:
            M5.update()


def main():
    if not device.is_micropython():
        M5.begin()
        import file_mock
        import colours

        print("Mock file operations")
        with file_mock.do():
            for num, colour, strategy in zip(
                range(6), colours.PLAYER_COLOURS, logic.Strategies.ALL
            ):
                open(f"titable/player_{num + 1}_colour", "w").write(str(colour.id))
                open(f"titable/player_{num + 1}_strategy", "w").write(str(strategy))
            inner_main()
    else:
        inner_main()


if "__main__" == __name__:
    main()
