import globals


class PersonState(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._input_sleep = config["input_sleep"]

        await self.listen_state(self._state_callback_async,
                                entity="person")
        await self.listen_state(self._input_sleep_callback_async,
                                entity=self._input_sleep)

    async def _state_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        if new == "not_home":
            await self.common.send_state_async(entity, f"*{await self.friendly_name(entity)}* has left *{old}*.")
        else:
            await self.common.send_state_async(entity, f"*{await self.friendly_name(entity)}* is at *{new}*.")

    async def _input_sleep_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        if new == "on":
            await self.common.send_state_async(
                "person.mithras", f"Mithras is asleep.")
        else:
            await self.common.send_state_async(
                "person.mithras", f"Mithras is awake.")
