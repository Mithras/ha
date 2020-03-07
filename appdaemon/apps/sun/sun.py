import globals

drivewayLight = "light.driveway"


class Sun(globals.HassAsync):
    async def initialize(self):
        await self.run_at_sunset(self.__sunset_callback)
        await self.run_at_sunrise(self.__sunrise_callback)

    async def __sunset_callback(self, kwargs):
        if await self.get_state(drivewayLight) == "off":
            self.common.light_turn_nightlight(drivewayLight)

    async def __sunrise_callback(self, kwargs):
        self.common.light_turn_off(drivewayLight)
