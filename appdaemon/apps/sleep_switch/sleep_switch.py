import globals


class SleepSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.input = config["input"]
        unique_id = config["unique_id"]
        self.listen_event(self.single_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="single")

    def single_callback(self, event_name, data, kwargs):
        self.toggle(self.input)
