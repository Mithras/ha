import globals


class GlobalLight(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        input_sleep = config["input_sleep"]
        self.entities = config["entities"]

        await self.listen_state(self._state_callback_async,
                                entity="person",
                                old="home")
        await self.listen_state(self._input_sleep_callback_async,
                                entity=input_sleep)

    async def _state_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new or await self.anyone_home():
            return
        await self._turn_off_entities_async()

    async def _input_sleep_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new or new != "on":
            return
        await self._turn_off_entities_async()

    async def _turn_off_entities_async(self):
        for entity in self.entities:
            await self.common.turn_off_async(entity)
            await self.sleep(0.1)
