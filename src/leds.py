import os
import json

from colours import Colour
import colours

import device


class Lights:
    MAX_BRIGHTNESS = 100
    MODE_RELATIVE = "."
    MODE_ABSOLUTE = "/"

    KEY_GLOBAL_PERCENTAGE = "g_p"
    KEY_BRIGHTNESS = "b"
    KEY_MODE = "m"
    KEY_PERCENTAGE = "p"
    KEY_OVERRIDE = "o"
    KEY_COLOUR = "c"

    def __init__(self, override_url=None, only_print=False):
        self._override_url = override_url
        self._only_print = only_print
        self._config_url = "titable/url"
        self._config_lights = "titable/lights"
        loaded = False
        if device.file_exists_and_not_empty(self._config_url):
            try:
                self._url = open(self._config_url).read()
                loaded = True
            except:
                print(f"Invalid url file: {self._config_url}")
        if not loaded:
            self._url = "http://lights"
            device.create_file(self._config_url, self._url)
        loaded = False
        if device.file_exists_and_not_empty(self._config_lights):
            try:
                self._lights = json.loads(open(self._config_lights).read())
                loaded = True
            except:
                print(f"Invalid lights file: {self._config_lights}")
        if not loaded:
            self._lights = {
                Lights.KEY_GLOBAL_PERCENTAGE: 100,
                Lights.KEY_BRIGHTNESS: {},
            }
            device.create_file(self._config_lights, json.dumps(self._lights))
        self._changed = False
        self._last_data_str = None

    def write_config(self):
        print(self._lights)
        if self._changed:
            open(self._config_lights, "w").write(json.dumps(self._lights))

    def _send_command_raw(self, data: dict):
        data_str = json.dumps(data)
        if data_str == self._last_data_str:
            return
        else:
            self._last_data_str = data_str
        url = self._override_url if self._override_url else self._url
        if self._only_print:
            print(f"{url} -> {data_str}")
        else:
            requests2.post(url, json=data)

    def _send_command(self, r: int, g: int, b: int, state: str, brightness: int):
        data = {
            "state": state,
            "rgb": f"{r},{g},{b}",
            "brightness": str(brightness),
        }
        self._send_command_raw(data)

    def _adjust_light_and_send_command(self, state: str, colour: Colour):
        if colour:
            lightness = None
            if colour.key in self._lights[Lights.KEY_BRIGHTNESS]:
                conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
                if conf[Lights.KEY_MODE] == Lights.MODE_RELATIVE:
                    factor = (
                        conf[Lights.KEY_PERCENTAGE]
                        / 100
                        * self._lights[Lights.KEY_GLOBAL_PERCENTAGE]
                        / 100
                    )
                    print(f"relative, factor = {factor}")
                else:
                    factor = conf[Lights.KEY_PERCENTAGE] / 100
                    print(f"absolute, factor = {factor}")
                if Lights.KEY_OVERRIDE in conf:
                    lightness = conf[Lights.KEY_OVERRIDE]
                    print(f"override lightness: {lightness}")
            else:
                factor = self._lights[Lights.KEY_GLOBAL_PERCENTAGE] / 100
                print(f"global, factor = {factor}")
            if lightness is None:
                lightness = colour.get_perceived_lightness()
                print(f"compute lightness: {lightness}")
            brightness = min(Lights.MAX_BRIGHTNESS, int(lightness * factor))
            r, g, b = self._translate(colour)
            self._send_command(r, g, b, state, brightness)
        else:
            data = {
                "state": state,
            }
            self._send_command_raw(data)

    def _translate(self, colour: Colour):
        rgb = self.get_colour(colour)
        if rgb:
            return rgb
        else:
            return colour.r, colour.g, colour.b

    def set_absolute(self, colour: Colour):
        if colour.raw_int not in self._lights[Lights.KEY_BRIGHTNESS]:
            self._lights[Lights.KEY_BRIGHTNESS][colour.key] = {
                Lights.KEY_MODE: Lights.MODE_ABSOLUTE,
                Lights.KEY_PERCENTAGE: 1,
            }
            self._changed = True
        else:
            conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
            if (
                Lights.KEY_MODE not in conf
                or conf[Lights.KEY_MODE] != Lights.MODE_ABSOLUTE
            ):
                conf[Lights.KEY_MODE] = Lights.MODE_ABSOLUTE
                self._changed = True

    def set_relative(self, colour: Colour):
        if colour.raw_int not in self._lights[Lights.KEY_BRIGHTNESS]:
            self._lights[Lights.KEY_BRIGHTNESS][colour.key] = {
                Lights.KEY_MODE: Lights.MODE_ABSOLUTE,
                Lights.KEY_PERCENTAGE: 1,
            }
            self._changed = True
        else:
            conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
            if (
                Lights.KEY_MODE not in conf
                or conf[Lights.KEY_MODE] != Lights.MODE_ABSOLUTE
            ):
                conf[Lights.KEY_MODE] = Lights.MODE_ABSOLUTE
                self._changed = True

    def get_mode(self, colour: Colour) -> str:
        conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
        try:
            return conf[Lights.KEY_MODE]
        except KeyError:
            return None

    def get_percentage(self, colour: Colour) -> int:
        conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
        try:
            return conf[Lights.KEY_PERCENTAGE]
        except KeyError:
            return None

    def get_colour(self, colour: Colour) -> list[int]:
        conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
        try:
            return conf[Lights.KEY_COLOUR]
        except KeyError:
            return None

    def set_override(self, colour: Colour, lightness: int):
        if colour.key not in self._lights[Lights.KEY_BRIGHTNESS]:
            self._lights[Lights.KEY_BRIGHTNESS][colour.key] = {
                Lights.KEY_PERCENTAGE: 100,
                Lights.KEY_MODE: Lights.MODE_RELATIVE,
                Lights.KEY_OVERRIDE: lightness,
            }
            self._changed = True
        else:
            conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
            if (
                Lights.KEY_PERCENTAGE not in conf
                or conf[Lights.KEY_PERCENTAGE] != lightness
            ):
                conf[Lights.KEY_PERCENTAGE] = lightness
                self._changed = True

    def set_percentage(self, colour: Colour, percentage: int):
        if colour.key not in self._lights[Lights.KEY_BRIGHTNESS]:
            self._lights[Lights.KEY_BRIGHTNESS][colour.key] = {
                Lights.KEY_PERCENTAGE: percentage,
                Lights.KEY_MODE: Lights.MODE_RELATIVE,
            }
            self._changed = True
        else:
            conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
            conf[Lights.KEY_PERCENTAGE] = percentage
            if (
                Lights.KEY_PERCENTAGE not in conf
                or conf[Lights.KEY_PERCENTAGE] != percentage
            ):
                conf[Lights.KEY_PERCENTAGE] = percentage
                self._changed = True

    def set_colour(self, colour: Colour, rgb: list[int]):
        if colour.key not in self._lights[Lights.KEY_BRIGHTNESS]:
            self._lights[Lights.KEY_BRIGHTNESS][colour.key] = {
                Lights.KEY_PERCENTAGE: 100,
                Lights.KEY_MODE: Lights.MODE_RELATIVE,
                Lights.KEY_COLOUR: rgb,
            }
            self._changed = True
        else:
            conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
            if Lights.KEY_COLOUR not in conf or conf[Lights.KEY_COLOUR] != rgb:
                conf[Lights.KEY_COLOUR] = rgb
                self._changed = True

    def inc_percentage(self, colour: Colour, delta_percentage: int):
        if colour.key not in self._lights[Lights.KEY_BRIGHTNESS]:
            self._lights[Lights.KEY_BRIGHTNESS][colour.key] = {
                Lights.KEY_PERCENTAGE: 100 + delta_percentage,
                Lights.KEY_MODE: Lights.MODE_RELATIVE,
            }
        else:
            conf = self._lights[Lights.KEY_BRIGHTNESS][colour.key]
            if Lights.KEY_PERCENTAGE not in conf:
                conf[Lights.KEY_PERCENTAGE] = 100
            conf[Lights.KEY_PERCENTAGE] += delta_percentage
        self._changed = True

    def turn_on(self, colour: Colour):
        self._adjust_light_and_send_command("turn_on", colour)

    def turn_off(self):
        self._adjust_light_and_send_command("turn_off", None)

    def toggle(self, colour: Colour):
        self._adjust_light_and_send_command("toggle", colour)


def main():
    import time

    lights = Lights(only_print=False)
    lights.set_override(colours.PLAYER_BLACK, 75)
    lights.set_percentage(colours.PLAYER_BLUE, 250)
    lights.set_percentage(colours.PLAYER_GREEN, 200)
    lights.set_percentage(colours.PLAYER_ORANGE, 85)
    lights.set_percentage(colours.PLAYER_YELLOW, 90)
    lights.set_percentage(colours.PLAYER_PURPLE, 200)
    lights.set_percentage(colours.PLAYER_PINK, 70)
    lights.set_colour(colours.PLAYER_ORANGE, [255, 165, 0])
    lights.set_colour(colours.PLAYER_PINK, [255, 174, 160])
    lights.set_colour(colours.PLAYER_RED, [169, 34, 34])
    lights.set_colour(colours.PLAYER_PURPLE, [83, 31, 185])
    lights.write_config()
    if False:
        while True:
            lights.turn_on(colours.PLAYER_YELLOW)
            time.sleep(2)
            lights.turn_on(colours.PLAYER_BLUE)
            time.sleep(2)
            lights.turn_on(colours.PLAYER_BLACK)
            time.sleep(2)
            lights.turn_on(colours.PLAYER_GREEN)
            time.sleep(2)
            lights.turn_on(colours.PLAYER_ORANGE)
            time.sleep(2)
    else:
        while True:
            for colour in colours.PLAYER_COLOURS:
                print(
                    f"{colour} | {colour.raw_int} -> {colour.get_perceived_lightness()}"
                )
                lights.turn_on(colour)
                time.sleep(2)


if "__main__" == __name__:
    main()
