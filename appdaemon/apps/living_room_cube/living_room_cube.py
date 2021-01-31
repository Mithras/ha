import globals
from common import Profile, LIGHT_PROFILES


ROTATE_PROFILES = [
    ("Nightlight", "off"),
    ("Dimmed", "Nightlight"),
    ("Bright", "Dimmed"),
    ("Bright", "Bright"),
]


class LivingRoomCube(globals.Hass):
    async def initialize(self):
        await globals.Hass.initialize(self)

        config = self.args["config"]
        unique_id = config["unique_id"]
        digital_id = config["digital_id"]
        analog_id = config["analog_id"]
        self._light_kitchen = config["light_kitchen"]
        self._light_kitchen_app = config["light_kitchen_app"]
        self._light_living_room_main = config["light_living_room_main"]
        self._light_living_room_back = config["light_living_room_back"]
        self._light_kitchen_main = config["light_kitchen_main"]

        light_profiles_map = {
            x.profile: x
            for x in LIGHT_PROFILES
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

        await self.listen_event(self._digital_event_callback_async,
                                event="deconz_event",
                                unique_id=unique_id,
                                id=digital_id)
        await self.listen_event(self._analog_event_callback_async,
                                event="deconz_event",
                                unique_id=unique_id,
                                id=analog_id)

    async def _digital_event_callback_async(self, event_name, data, kwargs):
        event = self.common.get_cube_digital_event(data)
        if event == "flip_90":
            await self._flip_90_async()
        elif event == "flip_180":
            await self._flip_180_async()
        elif event == "double_tap":
            await self._double_tap_async()
        elif event == "shake":
            await self._shake_async()

    async def _analog_event_callback_async(self, event_name, data, kwargs):
        event = self.common.get_cube_analog_event(data)
        if event == "rotate_left":
            await self._rotate_profile_async(-1)
        elif event == "rotate_right":
            await self._rotate_profile_async(1)

    async def _flip_90_async(self):
        if await self.get_state(self._light_kitchen) == "off":
            await self.common.light_turn_bright_async(self._light_kitchen)
        else:
            await self.common.turn_off_async(self._light_kitchen)

    async def _flip_180_async(self):
        await self.call_service("appdaemon_app/toggle",
                                entity_id=self._light_kitchen_app)

    async def _rotate_profile_async(self, shift: int):
        main_weights = await self.common.get_light_profile_weights_async(
            self._light_living_room_main, self.rotate_profiles_main)
        back_weights = await self.common.get_light_profile_weights_async(
            self._light_living_room_back, self.rotate_profiles_back)

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
        await self.common.light_turn_profile_async(
            self._light_living_room_main, main_profile)
        await self.common.light_turn_profile_async(
            self._light_living_room_back, back_profile)

    async def _double_tap_async(self):
        if await self.get_state(self._light_living_room_main) != "off" or await self.get_state(self._light_living_room_back) != "off":
            await self.common.turn_off_async(self._light_living_room_main)
            await self.common.turn_off_async(self._light_living_room_back)
        else:
            await self.common.light_turn_bright_async(self._light_living_room_main)
            await self.common.light_turn_bright_async(self._light_living_room_back)

    async def _shake_async(self):
        await self.call_service("light/toggle",
                                entity_id=self._light_kitchen_main)
