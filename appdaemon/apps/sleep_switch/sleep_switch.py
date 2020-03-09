import globals


class SleepSwitch(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._input = config["input"]
        unique_id = config["unique_id"]

        await self.listen_event(self._deconz_event_callback_async,
                                event="deconz_event",
                                unique_id=unique_id)

    async def _deconz_event_callback_async(self, event_name, data, kwargs):
        event, button = self.common.get_deconz_event(data)
        if event == "release_after_press" and button == 1:
            await self.call_service("input_boolean/toggle",
                                    entity_id=self._input)
