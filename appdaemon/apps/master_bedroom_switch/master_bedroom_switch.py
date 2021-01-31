import globals
from common import RELEASE_AFTER_PRESS, HOLD


class MasterBedroomSwitch(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        unique_id = config["unique_id"]
        self._master_bedroom_light = config["master_bedroom_light"]
        self.light_app_state = config["light_app_state"]

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
                await self.common.turn_off_async(self._master_bedroom_light)
        elif event == "hold":
            if button == 1:
                await self.common.light_turn_bright_async(self._master_bedroom_light)
            elif button == 2:
                full_state = await self.get_state(self.light_app_state, attribute="all")
                state, attributes = full_state["state"], full_state["attributes"]
                await self.set_state(self.light_app_state,
                                     state="on" if state != "on" else "off",
                                     attributes=attributes)
                if state == "on":
                    await self.common.light_flash(self._master_bedroom_light)
                else:
                    await self.common.light_flash(self._master_bedroom_light)
                    await self.sleep(0.5)
                    await self.common.light_flash(self._master_bedroom_light)
