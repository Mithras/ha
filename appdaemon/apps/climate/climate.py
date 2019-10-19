import globals


SET_HOME_CMD = "/climate-set-home"
DO_NOTHING_CMD = "/climate-do-nothing"


class Climate(globals.Hass):
    override = None

    def initialize(self):
        config = self.args["config"]
        self.cooling = config["cooling"]
        self.heating = config["heating"]
        self.temperature = config["temperature"]
        self.person = config["person"]
        self.home_params = config["home_params"]
        self.not_home_params = config["not_home_params"]
        self.sleep_params = config["sleep_params"]

        self.listen_state(self.device_tracker_callback,
                          entity="device_tracker")
        self.listen_state(self.sleep_input_callback,
                          entity=config["sleep_input"])

        self.listen_state(self.person_home_callback,
                          entity=self.person,
                          new="home")
        self.listen_state(self.person_not_home_callback,
                          entity=self.person,
                          new="not_home")

        self.listen_event(self.telegram_callback, "telegram_callback")

    def device_tracker_callback(self, entity, attribute, old, new, kwargs):
        if old != new:
            self.update_climate()

    def sleep_input_callback(self, entity, attribute, old, new, kwargs):
        if old != new:
            self.update_climate()

    def person_home_callback(self, entity, attribute, old, new, kwargs):
        if old != new:
            self.override = None

    def person_not_home_callback(self, entity, attribute, old, new, kwargs):
        if old != new and old != "home":
            hvac_mode = self.get_state(self.cooling)
            if(hvac_mode != "off"):
                return
            temperature = self.get_state(self.temperature)
            self.call_service("telegram_bot/send_message",
                              target=[self.common.telegram_debug_chat],
                              message=f"You have left *{old}*. Do you want to pre-set climate to home?\n  - current Temperature: {temperature}°C",
                              inline_keyboard=[[["Yes", SET_HOME_CMD], ["No", DO_NOTHING_CMD]]])

    def telegram_callback(self, event_name, data, kwargs):
        telegram_data = data["data"]
        telegram_id = data["id"]
        telegram_chat_id = data["chat_id"]
        telegram_message_id = data["message"]["message_id"]
        telegram_text = data["message"]["text"]

        self.log(f"telegram_callback: data={data}")

        if telegram_data == DO_NOTHING_CMD:
            self.telegram_edit_message(
                telegram_chat_id, telegram_message_id, f"{telegram_text}\n(*No*)")
            return

        if telegram_data == SET_HOME_CMD:
            self.telegram_edit_message(
                telegram_chat_id, telegram_message_id, f"{telegram_text}\n(*Yes*)")
            self.override = self.home_params
            self.update_climate()
            self.call_service("telegram_bot/answer_callback_query",
                              message=f"Climate has been pre-set to home.",
                              callback_query_id=telegram_id)

    def telegram_edit_message(self, telegram_chat_id, telegram_message_id, telegram_message):
        self.call_service("telegram_bot/edit_message",
                          chat_id=telegram_chat_id,
                          message_id=telegram_message_id,
                          message=telegram_message,
                          inline_keyboard=[])

    def update_climate(self):
        params = self.getParams()
        hvac_mode = params["hvac_mode"]
        low_temperature = params.get("low_temperature", None)
        high_temperature = params.get("high_temperature", None)

        self.log(
            f"update_climate: hvac_mode={hvac_mode}, low_temperature={low_temperature}, high_temperature={high_temperature}")
        if low_temperature is not None:
            self.call_service("climate/set_temperature",
                              entity_id=self.heating,
                              temperature=low_temperature)
        if high_temperature is not None:
            self.call_service("climate/set_temperature",
                              entity_id=self.cooling,
                              temperature=high_temperature)
        self.call_service("climate/set_hvac_mode",
                          entity_id=self.cooling,
                          hvac_mode=hvac_mode)

    def getParams(self):
        if self.override is not None:
            return self.override
        if self.noone_home():
            return self.not_home_params
        if self.common.is_sleep():
            return self.sleep_params
        return self.home_params
