import appdaemon.plugins.hass.hassapi as hass
import csv
from collections import namedtuple


def xy_color_to_weight(xy_color: float) -> int:
    return int(xy_color * 1000)


Profile = namedtuple(
    "Profile", ["profile", "x_weight", "y_weight", "brightness", "color_temp"])
with open("/config/light_profiles.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    LIGHT_PROFILES = [Profile(row[0], xy_color_to_weight(float(row[1])), xy_color_to_weight(
        float(row[2])), int(row[3]), int(row[4])) for row in csv_reader]


class Common(hass.Hass):
    def initialize(self):
        config = self.args["config"]
        self.telegram_mithras = config["telegram_mithras"]
        self.telegram_debug_chat = config["telegram_debug_chat"]
        self.telegram_location_chat = config["telegram_location_chat"]
        self.telegram_alarm_chat = config["telegram_alarm_chat"]
        self.http_base_url = config["http_base_url"]

    def is_sleep(self):
        return self.get_state(entity="input_boolean.sleep") == "on"

    def escapeMarkdown(self, string: str):
        return string.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

    def send_location(self, message: str, **kwargs):
        parse_mode = kwargs.get("parse_mode", "markdown")
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_location_chat],
                          message=message,
                          parse_mode=parse_mode)

    def send_alarm(self, message: str, **kwargs):
        parse_mode = kwargs.get("parse_mode", "markdown")
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_debug_chat],
                          message=message,
                          parse_mode=parse_mode)

    def send_debug(self, message: str, **kwargs):
        parse_mode = kwargs.get("parse_mode", "markdown")
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_debug_chat],
                          message=message,
                          parse_mode=parse_mode)

    def light_turn_bright(self, light_group: str):
        self.light_turn_profile(light_group, "Bright")

    def light_turn_dimmed(self, light_group: str):
        self.light_turn_profile(light_group, "Dimmed")

    def light_turn_nightlight(self, light_group: str):
        self.light_turn_profile(light_group, "Nightlight")

    def light_turn_profile(self, light_group: str, profile: str):
        self.call_service("light/turn_on",
                          entity_id=light_group,
                          profile=profile)

    def light_turn_off(self, light_group: str):
        self.call_service("light/turn_off",
                          entity_id=light_group)

    def get_profile(self, light_group):
        state = self.get_state(light_group, attribute="all")
        if state["state"] == "off":
            return "Off"
        attributes = state["attributes"]
        brightness = attributes["brightness"]
        color_temp = attributes.get("color_temp", None)
        if color_temp is None:
            x_color, y_color = attributes.get("xy_color", [None, None])
            x_weight = xy_color_to_weight(x_color)
            y_weight = xy_color_to_weight(y_color)
            return sorted(LIGHT_PROFILES, key=lambda profile:
                          abs(profile.x_weight - x_weight) +
                          abs(profile.y_weight - y_weight) +
                          abs(profile.brightness - brightness))[0].profile
        else:
            return sorted(LIGHT_PROFILES, key=lambda profile:
                          abs(profile.color_temp - color_temp) +
                          abs(profile.brightness - brightness))[0].profile
