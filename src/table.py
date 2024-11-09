import logic
import screens
from screens import ScreenTypes


class Titable:
    def __init__(self):
        self._game = logic.Game()
        self._screens = []
        self._current_screen_type = ScreenTypes.WELCOME
        self._current_screen = screens.ScreenWelcome()
        self._current_screen.draw()

    def touch(self, x: int, y: int):
        self._current_screen.touch(x, y)


def main():
    titable = Titable()


if "__main__" == __name__:
    main()
