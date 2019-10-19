import globals


class SleepSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.input = config["input"]
        self.listen_event(self.on_click_callback,
                          event="deconz_event_custom",
                          entity_id=config["switch"],
                          button=1,
                          code="x002")

    def on_click_callback(self, event_name, data, kwargs):
        self.toggle(self.input)
