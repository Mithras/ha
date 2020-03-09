import globals


class MasterBedroomSwitch(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        unique_id = config["unique_id"]
        self._master_bedroom_light = config["master_bedroom_light"]

        await self.listen_event(self._deconz_event_callback_async,
                                event="deconz_event",
                                unique_id=unique_id)

    async def _deconz_event_callback_async(self, event_name, data, kwargs):
        event, button = self.common.get_deconz_event(data)
        if event == "release_after_press":
            if button == 1:
                await self.common.light_turn_nightlight_async(
                    self._master_bedroom_light)
            elif button == 2:
                await self.common.light_turn_off_async(self._master_bedroom_light)
        elif event == "hold":
            await self.common.light_turn_bright_async(self._master_bedroom_light)
