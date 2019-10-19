import globals


class MasterBedroomSwitch(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.master_bedroom_light = config["master_bedroom_light"]
        self.master_bathroom_light = config["master_bathroom_light"]
        self.master_toilet_light = config["master_toilet_light"]

        self.listen_event(self.on_click_callback,
                          event="deconz_event_custom",
                          entity_id=config["switch"],
                          button=1,
                          code="x002")
        self.listen_event(self.on_hold_callback,
                          event="deconz_event_custom",
                          entity_id=config["switch"],
                          button=1,
                          code="x001")
        self.listen_event(self.off_click_callback,
                          event="deconz_event_custom",
                          entity_id=config["switch"],
                          button=2,
                          code="x002")
        self.listen_event(self.off_hold_callback,
                          event="deconz_event_custom",
                          entity_id=config["switch"],
                          button=2,
                          code="x001")

    def on_click_callback(self, event_name, data, kwargs):
        self.common.light_activate_nightlight(self.master_bedroom_light)
        self.common.light_activate_nightlight(self.master_bathroom_light)
        self.common.light_activate_nightlight(self.master_toilet_light)

    def on_hold_callback(self, event_name, data, kwargs):
        self.common.light_activate_bright(self.master_bedroom_light)

    def off_click_callback(self, event_name, data, kwargs):
        self.common.light_turn_off(self.master_bedroom_light)
        self.common.light_turn_off(self.master_bathroom_light)
        self.common.light_turn_off(self.master_toilet_light)

    def off_hold_callback(self, event_name, data, kwargs):
        self.common.light_activate_bright(self.master_bathroom_light)
        self.common.light_activate_bright(self.master_toilet_light)
