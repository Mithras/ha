import globals


class SleepSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.input = config["input"]
        unique_id = config["unique_id"]
        self.listen_event(self.single_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          command="release_after_press")

    def single_callback(self, event_name, data, kwargs):
        self.common.run_async(self.toggle,
                              self.input)
