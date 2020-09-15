import globals


AUTO_LOW = "Auto Low"
ON_LOW = "On Low"


class Ventilation(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._climate = config["climate"]
        self.on_low_interval = config["on_low_interval"]
        self.on_auto_interval = config["on_auto_interval"]
        self.check_interval = config["check_interval"]

        self.create_task(self._run())

    async def _run(self):
        mode = ON_LOW
        while True:
            interval = self.on_low_interval if mode == ON_LOW else self.on_auto_interval
            # self.log(
            #     f"_run: _mode = {mode}, interval = {interval}, check_interval = {self.check_interval}")
            i = 0
            while i < interval:
                # self.log(f"\t_run: i = {i}")
                await self._ensure_fan_mode(mode)
                sleep = min(interval - i, self.check_interval)
                # self.log(f"\t_run: sleep = {sleep}")
                await self.sleep(sleep)
                i += sleep
            mode = AUTO_LOW if mode == ON_LOW else ON_LOW

    async def _ensure_fan_mode(self, mode):
        fan_mode = await self.get_state(self._climate, "fan_mode")
        # self.log(f"\t_ensure_fan_mode: fan_mode = {fan_mode}, mode = {mode}")
        if fan_mode != mode:
            # self.log(f"\t_ensure_fan_mode: set_fan_mode = {mode}")
            await self.call_service("climate/set_fan_mode",
                                    entity_id=self._climate,
                                    fan_mode=mode)
