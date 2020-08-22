import globals


SET_HOME_CMD = "/climate-set-home"
DO_NOTHING_CMD = "/climate-do-nothing"


class Climate(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._climate = config["climate"]
        self._temperature = config["temperature"]
        self._person = config["person"]
        self._home_params = config["home_params"]
        self._not_home_params = config["not_home_params"]
        self._sleep_params = config["sleep_params"]
        self._override = None

        await self.listen_state(self._device_tracker_callback_async,
                                entity="device_tracker")
        await self.listen_state(self._sleep_input_callback_async,
                                entity=config["sleep_input"])

        await self.listen_state(self._person_home_callback_async,
                                entity=self._person,
                                new="home")
        await self.listen_state(self._person_not_home_callback_async,
                                entity=self._person,
                                new="not_home")

        await self.listen_event(self._telegram_callback_async, "telegram_callback")

    async def _device_tracker_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        await self._update_climate_async()

    async def _sleep_input_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        await self._update_climate_async()

    async def _person_home_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        self._override = None

    async def _person_not_home_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new or old == "home":
            return

        hvac_mode = await self.get_state(self._climate)
        target_temperature = await self.get_state(self._climate, "temperature")
        temperature = await self.get_state(self._temperature)
        if hvac_mode is None or target_temperature is None or temperature is None:
            return

        target_temperature_float = float(target_temperature)
        temperature_float = float(temperature)
        if self._home_params["hvac_mode"] == hvac_mode and self._home_params["temperature"] == target_temperature_float:
            return
        if self._home_params["hvac_mode"] == "heat" and self._home_params["temperature"] <= temperature_float:
            return
        if self._home_params["hvac_mode"] == "cool" and self._home_params["temperature"] >= temperature_float:
            return
        if self._home_params["hvac_mode"] == "heat_cool" and self._home_params["temperature"] == temperature_float:
            return

        await self.call_service("telegram_bot/send_message",
                                target=[self.common.telegram_debug_chat],
                                message=f"You have left *{old}*. Do you want to pre-set climate to home?\n  - current Temperature: {temperature_float}°C",
                                inline_keyboard=[[["Yes", SET_HOME_CMD], ["No", DO_NOTHING_CMD]]])

    async def _telegram_callback_async(self, event_name, data, kwargs):
        telegram_data = data["data"]
        telegram_id = data["id"]
        telegram_chat_id = data["chat_id"]
        telegram_message_id = data["message"]["message_id"]
        telegram_text = data["message"]["text"]

        if telegram_data == DO_NOTHING_CMD:
            await self._telegram_edit_message_async(
                telegram_chat_id, telegram_message_id, f"{telegram_text}\n(*No*)")
            return

        if telegram_data == SET_HOME_CMD:
            await self._telegram_edit_message_async(
                telegram_chat_id, telegram_message_id, f"{telegram_text}\n(*Yes*)")
            self._override = self._home_params
            await self._update_climate_async()
            await self.call_service("telegram_bot/answer_callback_query",
                                    message=f"Climate has been pre-set to home.",
                                    callback_query_id=telegram_id)

    async def _telegram_edit_message_async(self, telegram_chat_id, telegram_message_id, telegram_message):
        await self.call_service("telegram_bot/edit_message",
                                chat_id=telegram_chat_id,
                                message_id=telegram_message_id,
                                message=telegram_message,
                                inline_keyboard=[])

    async def _update_climate_async(self):
        params = await self._getParams_async()
        hvac_mode = params["hvac_mode"]
        temperature = params.get("temperature", None)

        await self.call_service("climate/set_hvac_mode",
                                entity_id=self._climate,
                                hvac_mode=hvac_mode)
        if temperature is not None:
            await self.call_service("climate/set_temperature",
                                    entity_id=self._climate,
                                    temperature=temperature)

    async def _getParams_async(self):
        if self._override is not None:
            return self._override
        if await self.noone_home():
            return self._not_home_params
        if await self.common.is_sleep_async():
            return self._sleep_params
        return self._home_params
