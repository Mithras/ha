import appdaemon.plugins.hass.hassapi as hass


class Common(hass.Hass):
    def initialize(self):
        config = self.args["config"]
        self.telegram_mithras = config["telegram_mithras"]
        self.telegram_debug_chat = config["telegram_debug_chat"]
        self.telegram_location_chat = config["telegram_location_chat"]
        self.telegram_alarm_chat = config["telegram_alarm_chat"]
        self.http_base_url = config["http_base_url"]

    def is_sleep(self):
        return self.get_state(entity="input_boolean.sleep") == "on"

    def escapeMarkdown(self, string: str):
        return string.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

    def send_location(self, message: str, **kwargs):
        parse_mode = kwargs.get("parse_mode", "markdown")
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_location_chat],
                          message=message,
                          parse_mode=parse_mode)

    def send_alarm(self, message: str, **kwargs):
        parse_mode = kwargs.get("parse_mode", "markdown")
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_debug_chat],
                          message=message,
                          parse_mode=parse_mode)

    def send_debug(self, message: str, **kwargs):
        parse_mode = kwargs.get("parse_mode", "markdown")
        self.call_service("telegram_bot/send_message",
                          target=[self.telegram_debug_chat],
                          message=message,
                          parse_mode=parse_mode)

    def light_activate_bright(self, lightGroup: str):
        self.light_activate_scene(lightGroup, "Bright")

    def light_activate_dimmed(self, lightGroup: str):
        self.light_activate_scene(lightGroup, "Dimmed")

    def light_activate_nightlight(self, lightGroup: str):
        self.light_activate_scene(lightGroup, "Nightlight")

    def light_activate_scene(self, lightGroup: str, scene: str):
        self.call_service("hue/hue_activate_scene",
                          group_name=self.friendly_name(lightGroup),
                          scene_name=scene)

    def light_turn_off(self, lightGroup: str):
        self.call_service("light/turn_off",
                          entity_id=lightGroup)
