import globals


class Sun(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self.light = config["light"]

        await self.run_at_sunset(self._sunset_callback_async)
        await self.run_at_sunrise(self._sunrise_callback_async)

    async def _sunset_callback_async(self, kwargs):
        if await self.get_state(self.light) == "off":
            await self.common.light_turn_nightlight_async(self.light)

    async def _sunrise_callback_async(self, kwargs):
        await self.common.turn_off_async(self.light)
