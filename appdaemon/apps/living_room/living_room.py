import globals


class LivingRoom(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._mithras_desktop = config["mithras_desktop"]
        self._jotunheim = config["jotunheim"]
        self._rokit6 = config["rokit6"]
        self._samsung_tv = config["samsung_tv"]
        self._living_room_main_light = config["living_room_main_light"]
        self._living_room_back_light = config["living_room_back_light"]
        self._light_strip = config["light_strip"]

        await self.listen_state(self._mithras_desktop_callback_async,
                                entity=self._mithras_desktop)
        await self.listen_state(self._person_home_callback_async,
                                entity=config["person"],
                                new="home")
        await self.listen_state(self._person_not_home_callback_async,
                                entity=config["person"],
                                new="not_home")
        await self.listen_state(self._awake_callback_async,
                                entity=config["sleep_input"],
                                new="off")

    async def _mithras_desktop_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        if new == "on":
            await self._activate_async()
        else:
            await self._deactivate_async()

    async def _person_home_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        await self._activate_async()
        await self.call_service("switch/turn_on",
                                entity_id=self._mithras_desktop)

    async def _person_not_home_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new or await self.anyone_home():
            return
        await self._deactivate_async()

    async def _awake_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        await self.call_service("switch/turn_on",
                                entity_id=self._mithras_desktop)

    async def _activate_async(self):
        await self.call_service("switch/turn_on",
                                entity_id=self._jotunheim)
        await self.call_service("switch/turn_on",
                                entity_id=self._rokit6)
        await self.call_service("media_player/turn_on",
                                entity_id=self._samsung_tv)
        await self.common.light_turn_bright_async(self._living_room_main_light)
        await self.common.light_turn_dimmed_async(self._living_room_back_light)

    async def _deactivate_async(self):
        await self.call_service("switch/turn_off",
                                entity_id=self._jotunheim)
        await self.call_service("switch/turn_off",
                                entity_id=self._rokit6)
        await self.call_service("media_player/turn_off",
                                entity_id=self._samsung_tv)
        await self.common.light_turn_off_async(self._living_room_main_light)
        await self.common.light_turn_off_async(self._living_room_back_light)
        await self.common.light_turn_off_async(self._light_strip)
