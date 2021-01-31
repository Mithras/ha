import globals


AUTO_LOW = "Auto Low"
ON_LOW = "On Low"


class Ventilation(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._climate = config["climate"]
        self._on_low_interval = config["on_low_interval"]
        self._on_auto_interval = config["on_auto_interval"]
        self._sleep_input = config["sleep_input"]

        self._fan_running = None
        self._timer_handle = None
        self._start_when_awake = False

        await self.listen_state(self._climate_callback_async,
                                entity=self._climate,
                                attribute="hvac_action")
        await self.listen_state(self._climate_callback_async,
                                entity=self._climate,
                                attribute="fan_mode")
        await self.listen_state(self._awake_callback_async,
                                entity=self._sleep_input,
                                new="off")
        await self._handle_climate_change_async()

    async def _climate_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        await self._handle_climate_change_async()

    async def _awake_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        if self._start_when_awake:
            self._start_when_awake = False
            await self.call_service("climate/set_fan_mode",
                                    entity_id=self._climate,
                                    fan_mode=ON_LOW)

    async def _handle_climate_change_async(self):
        hvac_action = await self.get_state(self._climate, attribute="hvac_action")
        fan_mode = await self.get_state(self._climate, attribute="fan_mode")
        fan_running = fan_mode == "On Low" or hvac_action != "idle"

        if self._fan_running == fan_running:
            return

        self._fan_running = fan_running
        delay = self._on_low_interval if self._fan_running else self._on_auto_interval
        await self.cancel_timer(self._timer_handle)
        self._timer_handle = await self.run_in(self._set_fan_mode, delay)

    async def _set_fan_mode(self, kwargs):
        fan_mode = AUTO_LOW if self._fan_running else ON_LOW
        if fan_mode == ON_LOW and await self.get_state(self._sleep_input) == "on":
            self._start_when_awake = True
            return
        await self.call_service("climate/set_fan_mode",
                                entity_id=self._climate,
                                fan_mode=fan_mode)
