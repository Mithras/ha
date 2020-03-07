import globals


class SleepSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.input = config["input"]
        unique_id = config["unique_id"]

        self.listen_event(self._callback,
                          event="deconz_event",
                          unique_id=unique_id)

    def _callback(self, event_name, data, kwargs):
        event, button = self.get_common().get_deconz_event(data)
        if event == "release_after_press" and button == 1:
            self.toggle(self.input)
