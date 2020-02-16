import appdaemon.plugins.hass.hassapi as hass
import csv
from collections import namedtuple


def xy_color_to_weight(xy_color: float) -> int:
    return int(xy_color * 1000)


Profile = namedtuple(
    "Profile", ["profile", "x_weight", "y_weight", "brightness", "color_temp"])
with open("/config/light_profiles.csv") as profiles_file:
    with open("/config/light_profile_temps.csv") as profile_temps_file:
        profiles_reader = csv.reader(profiles_file)
        profile_temps_reader = csv.reader(profile_temps_file)
        next(profiles_reader)
        next(profile_temps_reader)
        LIGHT_PROFILES = [Profile(row1[0], xy_color_to_weight(float(row1[1])), xy_color_to_weight(float(
            row1[2])), int(row1[3]), int(row2[1])) for row1, row2 in zip(profiles_reader, profile_temps_reader)]

CUBE_PUSH = (1000, 2000, 3000, 4000, 5000, 6000)
CUBE_DOUBLE_TAP = (1001, 2002, 3003, 4004, 5005, 6006)
CUBE_FLIP_180 = (1006, 2005, 3004, 4003, 5002, 6001)
CUBE_FLIP_90 = (1002, 1003, 1004, 1005, 2001, 2003, 2004, 2006, 3001, 3002, 3005,
                3006, 4001, 4002, 4005, 4006, 5001, 5003, 5004, 5006, 6002, 6003, 6004, 6005)
CUBE_SHAKE = (7007,)
CUBE_DROP = (7008,)
CUBE_WAKE = (7000,)

DECONZ_EVENTS = [
    "initial_press",
    "hold",
    "release_after_press",
    "release_after_hold",
    "double_press",
    "triple_press",
    "quadruple_press",
    "shake",
    "drop",
    "tilt",
    "many_press"
]


class Common(hass.Hass):
    def initialize(self):
        config = self.args["config"]
        self.telegram_mithras = config["telegram_mithras"]
        self.telegram_debug_chat = config["telegram_debug_chat"]
        self.telegram_location_chat_mithras = config["telegram_location_chat_mithras"]
        self.telegram_location_chat_diana = config["telegram_location_chat_diana"]
        self.telegram_alarm_chat = config["telegram_alarm_chat"]
        self.http_base_url = config["http_base_url"]

    def is_sleep(self):
        return self.get_state(entity="input_boolean.sleep") == "on"

    def escapeMarkdown(self, string: str):
        return string.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

    def send_location(self, person: str, message: str, **kwargs):
        if person == "person.mithras":
            target = self.telegram_location_chat_mithras
        elif person == "person.diana":
            target = self.telegram_location_chat_diana
        self.run_async(self.call_service,
                       "telegram_bot/send_message",
                       target=[target],
                       message=message,
                       **kwargs)

    def send_alarm(self, message: str, **kwargs):
        self.run_async(self.call_service,
                       "telegram_bot/send_message",
                       target=[self.telegram_debug_chat],
                       message=message,
                       **kwargs)

    def send_debug(self, message: str, **kwargs):
        self.run_async(self.call_service,
                       "telegram_bot/send_message",
                       target=[self.telegram_debug_chat],
                       message=message,
                       **kwargs)

    def light_turn_bright(self, light_group: str):
        self.light_turn_profile(light_group, "Bright")

    def light_turn_dimmed(self, light_group: str):
        self.light_turn_profile(light_group, "Dimmed")

    def light_turn_nightlight(self, light_group: str):
        self.light_turn_profile(light_group, "Nightlight")

    def light_turn_profile(self, light_group: str, profile: str):
        if profile == "off":
            self.light_turn_off(light_group)
        else:
            self.run_async(self.call_service,
                           "light/turn_on",
                           entity_id=light_group,
                           profile=profile)

    def light_turn_on(self, light_group: str):
        self.run_async(self.call_service,
                       "light/turn_on",
                       entity_id=light_group)

    def light_turn_off(self, light_group: str):
        self.run_async(self.call_service,
                       "light/turn_off",
                       entity_id=light_group)

    def get_light_profiles(self):
        return LIGHT_PROFILES

    def get_light_profile_weights(self, light_group, light_profiles=LIGHT_PROFILES):
        state_profile = self._get_light_profile(light_group)
        return [self._get_diff(state_profile, light_profile)
                for light_profile in light_profiles]

    def _get_diff(self, profileA, profileB):
        diff = abs(profileA.brightness - profileB.brightness)
        if profileA.color_temp is not None and profileB.color_temp is not None:
            diff += abs(profileA.color_temp - profileB.color_temp)
        elif profileA.color_temp is None != profileB.color_temp is None:
            diff += 1000
        if profileA.x_weight is not None and profileA.y_weight is not None and profileB.x_weight is not None and profileB.y_weight is not None:
            diff += abs(profileA.x_weight - profileB.x_weight)
            diff += abs(profileA.y_weight - profileB.y_weight)
        elif profileA.x_weight is None != profileA.y_weight is None or profileB.x_weight is None != profileB.y_weight is None:
            diff += 2000
        return diff

    def _get_light_profile(self, light_group):
        state = self.get_state(light_group, attribute="all")
        if state["state"] == "off":
            return Profile(None, None, None, 0, None)
        attributes = state["attributes"]
        brightness = attributes["brightness"]
        color_temp = attributes.get("color_temp", None)
        if color_temp is None:
            x_color, y_color = attributes.get("xy_color", [None, None])
            x_weight = xy_color_to_weight(x_color)
            y_weight = xy_color_to_weight(y_color)
            return Profile(None, x_weight, y_weight, brightness, None)
        else:
            return Profile(None, None, None, brightness, color_temp)

    def run_async(self, callback, *args, **kwargs):
        hass.Hass.run_in(self, self._run_async_callback, 0,
                         inner_callback=callback,
                         args=args,
                         kwargs=kwargs)

    def run_in(self, callback, delay, *args, **kwargs):
        hass.Hass.run_in(self, self._run_async_callback, delay,
                         inner_callback=callback,
                         args=args,
                         kwargs=kwargs)

    def get_deconz_event(self, data):
        event = data["event"]
        button = event // 1000
        code = event - button * 1000
        return (DECONZ_EVENTS[code], button)

    def get_cube_digital_event(self, data):
        event = data["event"]
        if event in CUBE_PUSH:
            return "push"
        if event in CUBE_DOUBLE_TAP:
            return "double_tap"
        if event in CUBE_FLIP_180:
            return "flip_180"
        if event in CUBE_FLIP_90:
            return "flip_90"
        if event in CUBE_SHAKE:
            return "shake"
        if event in CUBE_DROP:
            return "drop"
        if event in CUBE_WAKE:
            return "wake"

    def get_cube_analog_event(self, data):
        event = data["event"]
        if event < 0:
            return "rotate_left"
        return "rotate_right"

    def _run_async_callback(self, kwargs):
        callback = kwargs["inner_callback"]
        args = kwargs["args"]
        kwargs = kwargs["kwargs"]
        callback(*args, ** kwargs)
