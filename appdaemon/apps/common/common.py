import hassapi as hass
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

INITIAL_PRESS = "initial_press"
HOLD = "hold"
RELEASE_AFTER_PRESS = "release_after_press"
RELEASE_AFTER_HOLD = "release_after_hold"
DOUBLE_PRESS = "double_press"
TRIPLE_PRESS = "triple_press"
QUADRUPLE_PRESS = "quadruple_press"
SHAKE = "shake"
DROP = "drop"
TILT = "tilt"
MANY_PRESS = "many_press"
DECONZ_EVENTS = [
    INITIAL_PRESS,
    HOLD,
    RELEASE_AFTER_PRESS,
    RELEASE_AFTER_HOLD,
    DOUBLE_PRESS,
    TRIPLE_PRESS,
    QUADRUPLE_PRESS,
    SHAKE,
    DROP,
    TILT,
    MANY_PRESS
]


class Common(hass.Hass):
    async def initialize(self):
        config = self.args["config"]
        self.telegram_mithras = config["telegram_mithras"]
        self.telegram_debug_chat = config["telegram_debug_chat"]
        self.telegram_state_chat_mithras = config["telegram_state_chat_mithras"]
        self.telegram_state_chat_diana = config["telegram_state_chat_diana"]
        self.telegram_alarm_chat = config["telegram_alarm_chat"]
        self.external_url = config["external_url"]

    async def is_sleep_async(self):
        return await self.get_state("input_boolean.sleep") == "on"

    def escapeMarkdown(self, string: str):
        return string.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

    async def send_state_async(self, person: str, message: str, **kwargs):
        if person == "person.mithras":
            target = self.telegram_state_chat_mithras
        elif person == "person.diana":
            target = self.telegram_state_chat_diana
        await self.call_service("telegram_bot/send_message",
                                target=[target],
                                message=message,
                                **kwargs)

    async def send_alarm_async(self, message: str, **kwargs):
        await self.call_service("telegram_bot/send_message",
                                target=[self.telegram_debug_chat],
                                message=message,
                                **kwargs)

    async def send_debug_async(self, message: str, **kwargs):
        await self.call_service("telegram_bot/send_message",
                                target=[self.telegram_debug_chat],
                                message=message,
                                **kwargs)

    async def light_turn_bright_async(self, light_group: str):
        await self.light_turn_profile_async(light_group, "Bright")

    async def light_turn_dimmed_async(self, light_group: str):
        await self.light_turn_profile_async(light_group, "Dimmed")

    async def light_turn_nightlight_async(self, light_group: str):
        await self.light_turn_profile_async(light_group, "Nightlight")

    async def light_turn_profile_async(self, light_group: str, profile: str):
        if profile == "off":
            await self.light_turn_off_async(light_group)
        else:
            await self.call_service("light/turn_on",
                                    entity_id=light_group,
                                    profile=profile)

    async def light_turn_on_async(self, light_group: str):
        await self.call_service("light/turn_on",
                                entity_id=light_group)

    async def light_turn_off_async(self, light_group: str):
        await self.call_service("light/turn_off",
                                entity_id=light_group)

    async def light_flash(self, light_group: str, flash="short"):
        await self.call_service("light/turn_on",
                                entity_id=light_group,
                                flash=flash)

    async def get_light_profile_weights_async(self, light_group, light_profiles=LIGHT_PROFILES):
        state_profile = await self._get_light_profile_async(light_group)
        return [self._get_diff(state_profile, light_profile)
                for light_profile in light_profiles]

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

    async def _get_light_profile_async(self, light_group):
        state = await self.get_state(light_group, attribute="all")
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
