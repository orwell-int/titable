import logic
import screens
from screens import ScreenTypes

import device
import M5
import time


class Titable:
    def __init__(self):
        self._game = logic.Game()
        self._screens = []
        self._current_screen_type = ScreenTypes.WELCOME
        self._current_screen = None
        self.switch_to_screen_welcome()

    def touch(self, x: int, y: int):
        self._current_screen.touch(x, y)

    def switch_to_screen_welcome(self):
        print("switch_to_screen_welcome")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenWelcome()
        self._current_screen._button_setup.action = self.switch_to_screen_setup
        self._current_screen.draw()


    def switch_to_screen_setup(self):
        print("switch_to_screen_setup")
        self._current_screen.hide()
        self._current_screen = screens.ScreenSetup(self._game.players)
        self._current_screen._button_return.action = self.switch_to_screen_welcome
        self._current_screen.draw()


def main():
    if not device.is_micropython():
        M5.begin()
    titable = Titable()
    if not device.is_micropython():
        M5.TITABLE = titable
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


if "__main__" == __name__:
    main()
