import globals


class Location(globals.Hass):
    async def initialize(self):
        await self.listen_state(self._state_callback_async,
                                entity="person")

    async def _state_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        if new == "not_home":
            await self.common.send_location_async(entity, f"*{await self.friendly_name(entity)}* has left *{old}*.")
        else:
            await self.common.send_location_async(entity, f"*{await self.friendly_name(entity)}* is at *{new}*.")
