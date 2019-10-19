import globals

drivewayLight = "light.driveway"


class Sun(globals.Hass):
    def initialize(self):
        self.run_at_sunset(self.sunset_callback)
        self.run_at_sunrise(self.sunrise_callback)

    def sunset_callback(self, kwargs):
        if self.get_state(entity=drivewayLight) == "off":
            self.common.light_activate_nightlight(drivewayLight)

    def sunrise_callback(self, kwargs):
        self.common.light_turn_off(drivewayLight)
