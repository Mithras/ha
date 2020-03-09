import globals


class Light(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._light_group = config["light_group"]
        self._sun_up_on_profile = config.get("sun_up_on_profile", None)
        self._sun_down_on_profile = config.get("sun_down_on_profile", None)
        self._sleep_on_profile = config.get("sleep_on_profile", None)
        self._sun_up_off_profile = config.get("sun_up_off_profile", None)
        self._sun_down_off_profile = config.get("sun_down_off_profile", None)
        self._sleep_off_profile = config.get("sleep_off_profile", None)
        self._ignore_sleep = config.get("ignore_sleep", False)
        self._sensorMap = {}

        for sensor in config["sensors"]:
            entity = sensor["entity"]
            additional_delay = sensor.get("additional_delay", None)
            self._sensorMap[entity] = {
                "state": None,
                "sleep_task": None
            }
            await self.listen_state(self._sensor_callback_async,
                                    entity=entity,
                                    additional_delay=additional_delay)

    async def _sensor_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        sensor = self._sensorMap[entity]

        if new == "on":
            self.log(f"callback.handle_on: sensor={sensor}")
            await self._handle_on_async(sensor)
        else:
            additional_delay = kwargs["additional_delay"]
            if additional_delay:
                self.log(
                    f"callback.sleep: sensor={sensor}, additional_delay={additional_delay}")
                sensor["sleep_task"] = self.create_task(
                    self.sleep(additional_delay))
                await sensor["sleep_task"]
            self.log(f"callback.handle_off: sensor={sensor}")
            await self._handle_off_async(sensor)

    async def _handle_on_async(self, sensor):
        if sensor["sleep_task"] is not None:
            sensor["sleep_task"].cancel()
            sensor["sleep_task"] = None
        sensor["state"] = True
        on_profile = await self._get_on_profile_async()
        self.log(f"\ton_profile={on_profile}")
        await self._handle_profile_async(self._light_group, on_profile)

    async def _handle_off_async(self, sensor):
        sensor["state"] = False
        if all(not sensor["state"] for sensor in self._sensorMap.values()):
            off_profile = await self._get_off_profile_async()
            self.log(f"\toff_profile={off_profile}")
            await self._handle_profile_async(self._light_group, off_profile)

    async def _get_on_profile_async(self):
        if not self._ignore_sleep and await self.common.is_sleep_async():
            return self._sleep_on_profile
        elif await self.sun_up():
            return self._sun_up_on_profile
        else:
            return self._sun_down_on_profile

    async def _get_off_profile_async(self):
        if not self._ignore_sleep and await self.common.is_sleep_async():
            return self._sleep_off_profile
        elif await self.sun_up():
            return self._sun_up_off_profile
        else:
            return self._sun_down_off_profile

    async def _handle_profile_async(self, light_group, profile):
        if profile == "on":
            await self.common.light_turn_on_async(light_group)
        elif profile == "off":
            await self.common.light_turn_off_async(light_group)
        elif profile is not None:
            await self.common.light_turn_profile_async(light_group, profile)
