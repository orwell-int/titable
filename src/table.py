import time

import logic
import screens
from screens import ScreenTypes
import events
import leds
import device

import M5


class Point:
    def __init__(self, num, round, turn, iteration, event, player_num):
        self.num = num
        self.round = round
        self.turn = turn
        self.iteration = iteration
        self.event = event
        self.player_num = player_num


class Titable:
    def __init__(self, leds_only_print=False, num_players: int = 6):
        if num_players == 0:
            path = "titable/num_players"
            if device.file_exists_and_not_empty(path):
                num_players = int(open(path, "r").read())
        if num_players != 0:
            self._game = logic.Game(num_players)
        else:
            self._game = None
        self._screens = {}
        self._current_screen = None
        self._saved_screen = None
        self._lights = leds.Lights(only_print=leds_only_print)
        self._play_event = None
        if num_players != 0:
            self.switch_to_screen_welcome()
        else:
            self.switch_to_screen_num_players()
        events.HANDLER.register(events.ALL, self)
        self._touched = False
        self._num_events = 0
        # self._history = []

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
            self.switch_to_screen_strategy_player(player)
        elif events.PICK_STRATEGY == event:
            pass
        elif events.SETUP_NAME == event:
            pass
        elif events.NEXT == event:
            self.next()
        elif events.PREVIOUS == event:
            self._play_event = None
            phase = args["phase"]
            self.previous(phase)
        elif events.PLAY_STRATEGY == event:
            self._play_event = event
        elif events.PLAY_TACTICAL_OR_COMPONENT == event:
            self._play_event = event
        elif events.PLAY_SKIP == event:
            self._play_event = event
        elif events.PLAY_PASS == event:
            self._play_event = event
        elif events.RESET_PHASE == event:
            pass
        elif events.RESET_ROUND == event:
            pass
        elif events.WELCOME == event:
            self._game.stop_playing()
            self.switch_to_screen_welcome()
        elif events.SAVE_SCREEN == event:
            if self._current_screen:
                self._saved_screen = self._current_screen.screen_type
            else:
                print("Unable to save current screen (None)")
        elif events.UNSAVE_SCREEN == event:
            self._saved_screen = None
        elif events.SELECT_NUM_PLAYERS == event:
            num_players = args["num_players"]
            device.create_file("titable/num_players", str(num_players))
            self._game = logic.Game(num_players)
            self.switch_to_screen_welcome()

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

    def switch_to_screen_num_players(self):
        print("switch_to_screen_num_players")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenNumPlayer(self._lights)
        self._current_screen.draw()

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
            self.switch_to_screen_strategy()
        elif logic.Game.PHASE_ACTION == phase:
            self.switch_to_screen_action()
        elif logic.Game.PHASE_AGENDA == phase:
            self.switch_to_screen_agenda()
        elif logic.Game.PHASE_STATUS == phase:
            self.switch_to_screen_status()
        else:
            raise Exception(f"Not implemented yet (resume_play from phase {phase})")

    def switch_to_screen_strategy(self):
        print("switch_to_screen_strategy")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenStrategy(self._lights, self._game)
        self._current_screen.draw()

    def switch_to_screen_strategy_player(self, player):
        print("switch_to_screen_strategy_player")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenStrategyPlayer(
            self._lights, self._game, player.num
        )
        self._current_screen.draw()

    def next(self):
        print("Table.next... with phase:", self._game.phase)
        phase = self._game.next(self._play_event)
        self._play_event = None
        if logic.Game.PHASE_ACTION == phase:
            self.switch_to_screen_action()
        elif logic.Game.PHASE_AGENDA == phase:
            self.switch_to_screen_agenda()
        elif logic.Game.PHASE_STATUS == phase:
            self.switch_to_screen_status()
        elif logic.Game.PHASE_STRATEGY == phase:
            self.switch_to_screen_strategy()
        else:
            raise Exception("Not implemented")

    def previous(self, phase):
        print(f"Table.previous({phase})...")
        if logic.Game.PHASE_STRATEGY == phase:
            self._game.previous()
            self.switch_to_screen_strategy()
        elif logic.Game.PHASE_ACTION == phase:
            self._game.previous()
            self.switch_to_screen_action()
        elif logic.Game.PHASE_STATUS == phase:
            self._game.previous()
            self.switch_to_screen_status()
        else:
            print(f"Phase not handled {phase}")

    def switch_to_screen_action(self):
        print("switch_to_screen_action")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenAction(self._lights, self._game)
        self._current_screen.draw()

    def switch_to_screen_agenda(self):
        print("switch_to_screen_agenda")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenAgenda(self._lights, self._game)
        self._current_screen.draw()

    def switch_to_screen_status(self):
        print("switch_to_screen_status")
        if self._current_screen:
            self._current_screen.hide()
        self._current_screen = screens.ScreenStatus(self._lights, self._game)
        self._current_screen.draw()

    def switch_to_screen_menu(self):
        print("switch_to_screen_menu")
        if self._current_screen:
            self._current_screen.hide()
        if self._saved_screen is None:
            self._saved_screen = self._current_screen.screen_type
        self._current_screen = screens.ScreenMenu(self._lights)
        self._current_screen.draw()

    def switch_to_previous_screen(self, return_screen=None):
        print(f"switch_to_previous_screen({return_screen})")
        assert self._current_screen is not None
        if return_screen is None:
            return_screen = self._current_screen.on_return
            print(f"switch_to_previous_screen -> {return_screen}")
        if ScreenTypes.SAVED_SCREEN == return_screen:
            return_screen = self._saved_screen
        if ScreenTypes.WELCOME == return_screen:
            self.switch_to_screen_welcome()
        elif ScreenTypes.SETUP_PLAYERS == return_screen:
            self.switch_to_screen_setup()
        elif ScreenTypes.SETUP_PLAYER_NAME == return_screen:
            raise Exception("It is not possible to switch back to SETUP_PLAYER_NAME")
        elif ScreenTypes.SETUP_PLAYER_COLOUR == return_screen:
            raise Exception("It is not possible to switch back to SETUP_PLAYER_COLOUR")
        elif ScreenTypes.STRATEGY_MAIN == return_screen:
            self.switch_to_screen_strategy()
        elif ScreenTypes.STRATEGY_PLAYER == return_screen:
            raise Exception("It is not possible to switch back to STRATEGY_PLAYER")
        elif ScreenTypes.ACTION_PLAYER == return_screen:
            self.switch_to_screen_action()
        elif ScreenTypes.AGENDA == return_screen:
            self.switch_to_screen_agenda()
        elif ScreenTypes.STATUS_PLAYER == return_screen:
            self.switch_to_screen_status()
        elif ScreenTypes.MENU == return_screen:
            self.switch_to_screen_menu()
        else:
            raise Exception("Unhandled (return) screen type:", return_screen)

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

    # def _append_event(self, event, player_num=None):
    #     self._num_events += 1
    #     parts = (self._game.round, self._game.turn, self._game.iteration, event)
    #     self._history.append(Point(self._num_events, *parts, player_num))
    #     path = "titable/events/" + str(self._num_events)
    #     content = [str(x) for x in parts]
    #     if player_num:
    #         content.append(str(player_num))
    #     device.create_file(path, "\n".join(content))


def inner_main():
    titable = Titable(leds_only_print=True, num_players=0)
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

        force_file_mock = False
        if force_file_mock:
            # This was copied from the command line after
            # setting PRINT_DATA to True in file_mock
            # (and reformatted)
            file_mock.CONTENT = {
                "titable/player_1_colour": "0",
                "titable/1/player_1_strategy": "1",
                "titable/player_2_colour": "1",
                "titable/1/player_2_strategy": "2",
                "titable/player_3_colour": "2",
                "titable/1/player_3_strategy": "3",
                "titable/player_4_colour": "3",
                "titable/1/player_4_strategy": "4",
                "titable/player_5_colour": "4",
                "titable/1/player_5_strategy": "5",
                "titable/player_6_colour": "5",
                "titable/1/player_6_strategy": "6",
                "titable/url": "http://lights",
                "titable/lights": '{"g_p": 100, "b": {}}',
                "titable/num_players": "5",
                "titable/game_ds_2": '{"_state": 1, "_phase": 2, "_current_player": 1, "_next_player": 2, "6": 1, "7": 1, "8": 1}',
                "titable/game_stack": "15",
                "titable/game": "5, 0, 1, 2, 2, 1, 1, u, 2, 1, 3, -1, -1, 0, s, 1, 1, 1, 0, 0, 0, 0, 0",
                "titable/game_ds_3": '{"_iteration": 1, "_current_player": 2, "_previous_player": 1, "_next_player": 3, "_player_index_used_strategy": 0}',
                "titable/1/player_1_has_played_strategy": "True",
                "titable/game_ds_4": '{"_iteration": 2, "_current_player": 3, "_previous_player": 2, "_next_player": 4, "_player_index_used_strategy": 1}',
                "titable/1/player_2_has_played_strategy": "True",
                "titable/game_ds_5": '{"_iteration": 3, "_current_player": 4, "_previous_player": 3, "_next_player": 5, "_player_index_used_strategy": 2}',
                "titable/1/player_3_has_played_strategy": "True",
                "titable/game_ds_6": '{"_iteration": 4, "_current_player": 5, "_previous_player": 4, "_next_player": 1, "_player_index_used_strategy": 3}',
                "titable/1/player_4_has_played_strategy": "True",
                "titable/game_ds_7": '{"_turn": 2, "_iteration": 0, "_current_player": 1, "_previous_player": 5, "_next_player": 2, "_player_index_used_strategy": 4}',
                "titable/1/player_5_has_played_strategy": "True",
                "titable/game_ds_8": '{"_iteration": 1, "_current_player": 2, "_previous_player": 1, "_next_player": 3, "_player_index_passed": 0, "_player_index_used_strategy": null}',
                "titable/1/player_1_has_passed": "True",
                "titable/game_ds_9": '{"_iteration": 2, "_current_player": 3, "_previous_player": 2, "_next_player": 4, "_player_index_passed": 1, "_player_index_hidden": 0}',
                "titable/1/player_2_has_passed": "True",
                "titable/game_ds_10": '{"_iteration": 3, "_current_player": 4, "_previous_player": 3, "_next_player": 5, "_player_index_passed": 2, "_player_index_hidden": 1}',
                "titable/1/player_3_has_passed": "True",
                "titable/game_ds_11": '{"_iteration": 4, "_current_player": 5, "_previous_player": 4, "_player_index_passed": 3, "_player_index_hidden": 2}',
                "titable/1/player_4_has_passed": "True",
                "titable/game_ds_12": '{"_phase": 4, "_turn": 0, "_iteration": 0, "_player_index_passed": null, "_player_index_hidden": null}',
                "titable/1/player_5_has_passed": "True",
                "titable/game_ds_13": '{"_phase": 1, "_round": 2, "_turn": 1, "_previous_player": null}',
                "titable/2/player_1_strategy": "8",
                "titable/2/player_2_strategy": "7",
                "titable/2/player_3_strategy": "6",
                "titable/2/player_4_strategy": "5",
                "titable/2/player_5_strategy": "4",
                "titable/game_ds_14": '{"_phase": 2, "_current_player": 1, "_next_player": 2, "1": 1, "2": 1, "3": 1, "6": 0, "7": 0, "8": 0}',
                "titable/game_ds_15": '{"_iteration": 1, "_current_player": 2, "_previous_player": 1, "_next_player": 3, "_player_index_used_strategy": 0}',
                "titable/2/player_5_has_played_strategy": "True",
            }
            file_mock.STATS = {
                "titable/player_1_colour": 32768,
                "titable/1/player_1_strategy": 32768,
                "titable/player_2_colour": 32768,
                "titable/1/player_2_strategy": 32768,
                "titable/player_3_colour": 32768,
                "titable/1/player_3_strategy": 32768,
                "titable/player_4_colour": 32768,
                "titable/1/player_4_strategy": 32768,
                "titable/player_5_colour": 32768,
                "titable/1/player_5_strategy": 32768,
                "titable/player_6_colour": 32768,
                "titable/1/player_6_strategy": 32768,
                "titable/url": 32768,
                "titable/lights": 32768,
                "titable/num_players": 32768,
                "titable/game_ds_2": 32768,
                "titable/game_stack": 32768,
                "titable/game": 32768,
                "titable/game_ds_3": 32768,
                "titable/1/player_1_has_played_strategy": 32768,
                "titable/game_ds_4": 32768,
                "titable/1/player_2_has_played_strategy": 32768,
                "titable/game_ds_5": 32768,
                "titable/1/player_3_has_played_strategy": 32768,
                "titable/game_ds_6": 32768,
                "titable/1/player_4_has_played_strategy": 32768,
                "titable/game_ds_7": 32768,
                "titable/1/player_5_has_played_strategy": 32768,
                "titable/game_ds_8": 32768,
                "titable/1/player_1_has_passed": 32768,
                "titable/game_ds_9": 32768,
                "titable/1/player_2_has_passed": 32768,
                "titable/game_ds_10": 32768,
                "titable/1/player_3_has_passed": 32768,
                "titable/game_ds_11": 32768,
                "titable/1/player_4_has_passed": 32768,
                "titable/game_ds_12": 32768,
                "titable/1/player_5_has_passed": 32768,
                "titable/game_ds_13": 32768,
                "titable/2/player_1_strategy": 32768,
                "titable/2/player_2_strategy": 32768,
                "titable/2/player_3_strategy": 32768,
                "titable/2/player_4_strategy": 32768,
                "titable/2/player_5_strategy": 32768,
                "titable/game_ds_14": 32768,
                "titable/game_ds_15": 32768,
                "titable/2/player_5_has_played_strategy": 32768,
            }
        print("Mock file operations")
        with file_mock.do():
            if not force_file_mock:
                for num, colour, strategy in zip(
                    range(6), colours.PLAYER_COLOURS, logic.Strategies.ALL
                ):
                    open(f"titable/player_{num + 1}_colour", "w").write(str(colour.id))
                    if num > 0:
                        open(f"titable/1/player_{num + 1}_strategy", "w").write(
                            str(strategy)
                        )
            inner_main()
    else:
        inner_main()


if "__main__" == __name__:
    main()
