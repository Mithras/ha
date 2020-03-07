import globals


class MasterBedroomSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        unique_id = config["unique_id"]
        self.master_bedroom_light = config["master_bedroom_light"]

        self.listen_event(self._callback,
                          event="deconz_event",
                          unique_id=unique_id)

    def _callback(self, event_name, data, kwargs):
        event, button = self.get_common().get_deconz_event(data)
        if event == "release_after_press":
            if button == 1:
                self.get_common().light_turn_nightlight(self.master_bedroom_light)
            elif button == 2:
                self.get_common().light_turn_off(self.master_bedroom_light)
        elif event == "hold":
            self.get_common().light_turn_bright(self.master_bedroom_light)
