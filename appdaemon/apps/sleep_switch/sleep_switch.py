import globals


class SleepSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.input = config["input"]
        device_ieee = config["device_ieee"]
        self.listen_event(self.single_callback,
                          event="zha_event",
                          device_ieee=device_ieee,
                          command="single")

    def single_callback(self, event_name, data, kwargs):
        self.toggle(self.input)
