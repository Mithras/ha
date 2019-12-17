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
        self.light_kitchen = config["light_kitchen"]
        self.light_kitchen_app = config["light_kitchen_app"]
        self.light_living_room = config["light_living_room"]
        self.light_living_room_main = config["light_living_room_main"]
        self.light_living_room_back = config["light_living_room_back"]
        self.switch_fireplace = config["switch_fireplace"]

        self.light_profiles = [x for x in self.common.get_light_profiles() if x.profile in [
            "Bright", "Dimmed", "Nightlight"]]

        self.listen_event(self.flip_90_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="flip_90")
        self.listen_event(self.flip_180_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="flip_180")
        self.listen_event(self.rotate_left_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="rotate_left")
        self.listen_event(self.rotate_right_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="rotate_right")
        self.listen_event(self.double_tap_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="double_tap")
        self.listen_event(self.shake_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="shake")
        # self.listen_event(self.drop_callback,
        #                   event="deconz_event_custom",
        #                   unique_id=unique_id,
        #                   command="drop")
        # self.listen_event(self.push_callback,
        #                   event="deconz_event_custom",
        #                   unique_id=unique_id,
        #                   command="push")

    def flip_90_callback(self, event_name, data, kwargs):
        if self.get_state(self.light_kitchen) == "off":
            self.common.light_turn_bright(self.light_kitchen)
        else:
            self.common.light_turn_off(self.light_kitchen)

    def flip_180_callback(self, event_name, data, kwargs):
        self.toggle(self.light_kitchen_app)

    def rotate_left_callback(self, event_name, data, kwargs):
        self.rotate_profile(-1)

    def rotate_right_callback(self, event_name, data, kwargs):
        self.rotate_profile(1)

    def rotate_profile(self, shift: int):
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

    def double_tap_callback(self, event_name, data, kwargs):
        main_profile = self.common.get_light_profile(
            self.light_living_room_main, self.light_profiles)
        back_profile = self.common.get_light_profile(
            self.light_living_room_back, self.light_profiles)
        if main_profile != "Bright" or back_profile != "Bright":
            self.common.light_turn_bright(self.light_living_room)
        else:
            self.common.light_turn_off(self.light_living_room)

    def shake_callback(self, event_name, data, kwargs):
        self.toggle(self.switch_fireplace)

    # def drop_callback(self, event_name, data, kwargs):
    #     pass

    # def push_callback(self, event_name, data, kwargs):
    #     pass
