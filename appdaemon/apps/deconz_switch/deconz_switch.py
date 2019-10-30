import globals

CODE_COMMAND_MAP = {
    "000": "initial_press",
    "001": "hold",
    "002": "release_after_press",
    "003": "release_after_hold",
    "004": "double_press",
    "005": "triple_press",
    "006": "quadruple_press",
    "007": "shake",
    "008": "drop",
    "009": "tilt",
    "010": "many_press"
}


class DeconzSwitch(globals.Hass):
    def initialize(self):
        for entity in self.args["config"]:
            self.listen_event(self.callback,
                              event="deconz_event",
                              id=entity)

    def callback(self, event_name, data, kwargs):
        unique_id = data["unique_id"]
        deconz_event = str(data["event"])
        button = int(deconz_event[0])
        code = deconz_event[1:]
        self.fire_event("deconz_event_custom",
                        unique_id=unique_id,
                        button=button,
                        command=CODE_COMMAND_MAP[code])
