import globals


class MasterBedroomSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        unique_id = config["unique_id"]
        self.master_bedroom_light = config["master_bedroom_light"]
        self.master_bathroom_light = config["master_bathroom_light"]
        self.master_toilet_light = config["master_toilet_light"]

        self.listen_event(self.on_click_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          button=1,
                          command="release_after_press")
        self.listen_event(self.on_hold_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          button=1,
                          command="hold")
        self.listen_event(self.off_click_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          button=2,
                          command="release_after_press")
        self.listen_event(self.off_hold_callback,
                          event="deconz_event_custom",
                          unique_id=unique_id,
                          button=2,
                          command="hold")

    def on_click_callback(self, event_name, data, kwargs):
        self.common.light_turn_nightlight(self.master_bedroom_light)
        self.common.light_turn_nightlight(self.master_bathroom_light)
        self.common.light_turn_nightlight(self.master_toilet_light)

    def on_hold_callback(self, event_name, data, kwargs):
        self.common.light_turn_bright(self.master_bedroom_light)

    def off_click_callback(self, event_name, data, kwargs):
        self.common.light_turn_off(self.master_bedroom_light)
        self.common.light_turn_off(self.master_bathroom_light)
        self.common.light_turn_off(self.master_toilet_light)

    def off_hold_callback(self, event_name, data, kwargs):
        self.common.light_turn_bright(self.master_bathroom_light)
        self.common.light_turn_bright(self.master_toilet_light)
