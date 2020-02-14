import globals
from common import Profile


ROTATE_PROFILES = [
    ("Nightlight", "off"),
    ("Dimmed", "Nightlight"),
    ("Bright", "Dimmed"),
    ("Bright", "Bright"),
]


class LivingRoomCube(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        unique_id = config["unique_id"]
        digital_id = config["digital_id"]
        analog_id = config["analog_id"]
        self.light_kitchen = config["light_kitchen"]
        self.light_kitchen_app = config["light_kitchen_app"]
        self.light_living_room = config["light_living_room"]
        self.light_living_room_main = config["light_living_room_main"]
        self.light_living_room_back = config["light_living_room_back"]
        self.switch_fireplace = config["switch_fireplace"]

        light_profiles_map = {
            x.profile: x
            for x in self.common.get_light_profiles()
        }
        light_profiles_map["off"] = Profile("off", None, None, 0, None)
        self.rotate_profiles_main = [
            light_profiles_map.get(x[0])
            for x in ROTATE_PROFILES
        ]
        self.rotate_profiles_back = [
            light_profiles_map.get(x[1])
            for x in ROTATE_PROFILES
        ]

        self.listen_event(self._digital_event_callback,
                          event="deconz_event",
                          unique_id=unique_id,
                          id=digital_id)
        self.listen_event(self._analog_event_callback,
                          event="deconz_event",
                          unique_id=unique_id,
                          id=analog_id)

    def _digital_event_callback(self, event_name, data, kwargs):
        event = self.common.get_cube_digital_event(data)
        if event == "flip_90":
            self._flip_90()
        elif event == "flip_180":
            self._flip_180()
        elif event == "double_tap":
            self._double_tap()
        elif event == "shake":
            self._shake()

    def _analog_event_callback(self, event_name, data, kwargs):
        event = self.common.get_cube_analog_event(data)
        if event == "rotate_left":
            self._rotate_left()
        elif event == "rotate_right":
            self._rotate_right()

    def _flip_90(self):
        if self.get_state(self.light_kitchen) == "off":
            self.common.light_turn_bright(self.light_kitchen)
        else:
            self.common.light_turn_off(self.light_kitchen)

    def _flip_180(self):
        self.common.run_async(self.toggle,
                              self.light_kitchen_app)

    def _rotate_left(self):
        self._rotate_profile(-1)

    def _rotate_right(self):
        self._rotate_profile(1)

    def _rotate_profile(self, shift: int):
        main_weights = self.common.get_light_profile_weights(
            self.light_living_room_main, self.rotate_profiles_main)
        back_weights = self.common.get_light_profile_weights(
            self.light_living_room_back, self.rotate_profiles_back)

        weights = (main_weight+back_weight
                   for (main_weight, back_weight)
                   in zip(main_weights, back_weights))
        sorted_weights = sorted(
            enumerate(weights),
            key=lambda i_weight: i_weight[1])
        min_index = sorted_weights[0][0]
        index = min_index + shift
        index = min(max(0, index), len(ROTATE_PROFILES) - 1)

        # self.log(f"sorted_weights = {sorted_weights}")
        # self.log(f"min_index = {min_index}")
        # self.log(f"index = {index}")

        main_profile, back_profile = ROTATE_PROFILES[index]
        self.common.light_turn_profile(
            self.light_living_room_main, main_profile)
        self.common.light_turn_profile(
            self.light_living_room_back, back_profile)

    def _double_tap(self):
        if self.get_state(self.light_living_room) != "off":
            self.common.light_turn_off(self.light_living_room)
        else:
            self.common.light_turn_bright(self.light_living_room)

    def _shake(self):
        self.common.run_async(self.toggle,
                              self.switch_fireplace)
