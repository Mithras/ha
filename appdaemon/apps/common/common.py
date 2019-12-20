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


# TODO: run_in
# TODO: call_service_async
# TODO: turn_on / turn_off -> call_service_async
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
        self.call_service("telegram_bot/send_message",
                          target=[target],
                          message=message,
                          **kwargs)

    def send_alarm(self, message: str, **kwargs):
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_debug_chat],
                          message=message,
                          **kwargs)

    def send_debug(self, message: str, **kwargs):
        self.call_service("telegram_bot/send_message",
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
            self.call_service("light/turn_on",
                              entity_id=light_group,
                              profile=profile)

    def light_turn_off(self, light_group: str):
        self.call_service("light/turn_off",
                          entity_id=light_group)

    def get_light_profiles(self):
        return LIGHT_PROFILES

    def get_light_profile(self, light_group, light_profiles=LIGHT_PROFILES):
        state = self.get_state(light_group, attribute="all")
        if state["state"] == "off":
            return "off"
        attributes = state["attributes"]
        brightness = attributes["brightness"]
        color_temp = attributes.get("color_temp", None)
        if color_temp is None:
            x_color, y_color = attributes.get("xy_color", [None, None])
            x_weight = xy_color_to_weight(x_color)
            y_weight = xy_color_to_weight(y_color)
            return sorted(light_profiles, key=lambda profile:
                          abs(profile.x_weight - x_weight) +
                          abs(profile.y_weight - y_weight) +
                          abs(profile.brightness - brightness))[0].profile
        else:
            return sorted(light_profiles, key=lambda profile:
                          abs(profile.color_temp - color_temp) +
                          abs(profile.brightness - brightness))[0].profile
