import globals


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

        self.light_profiles = [x for x in self.common.get_light_profiles() if x.profile in [
            "Bright", "Dimmed", "Nightlight"]]

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
        main_profile = self.common.get_light_profile(
            self.light_living_room_main, self.light_profiles)
        back_profile = self.common.get_light_profile(
            self.light_living_room_back, self.light_profiles)
        # self.log(f"current: {main_profile} / {back_profile}")

        for i, (m, b) in enumerate(ROTATE_PROFILES):
            # self.log(f"\t i={i}, m={m}, b={b}")
            if main_profile == m and back_profile == b:
                i = i + shift
                break
        else:
            i = 0 if shift < 0 else len(ROTATE_PROFILES) - 1

        if i < 0 or i >= len(ROTATE_PROFILES):
            return
        new_main_profile, new_back_profile = ROTATE_PROFILES[i]
        # self.log(f"new: {new_main_profile} / {new_back_profile} (i={i})")
        self.common.light_turn_profile(
            self.light_living_room_main, new_main_profile)
        self.common.light_turn_profile(
            self.light_living_room_back, new_back_profile)

    def _double_tap(self):
        main_profile = self.common.get_light_profile(
            self.light_living_room_main, self.light_profiles)
        back_profile = self.common.get_light_profile(
            self.light_living_room_back, self.light_profiles)
        if main_profile != "Bright" or back_profile != "Bright":
            self.common.light_turn_bright(self.light_living_room)
        else:
            self.common.light_turn_off(self.light_living_room)

    def _shake(self):
        self.common.run_async(self.toggle,
                              self.switch_fireplace)
