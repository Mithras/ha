import globals


class Security(globals.Hass):
    def initialize(self):
        self.listen_state(self.state_callback,
                          entity="device_tracker")
        self.listen_state(self.state_callback,
                          entity="input_select.security_override")
        self.listen_state(self.state_callback,
                          entity="input_boolean.sleep")
        self.update_security()

    def state_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        self.update_security()

    def update_security(self):
        self.set_state("appdaemon.security", state=self.get_security())

    def get_security(self):
        security_override = self.get_state("input_select.security_override")
        if security_override != "Auto":
            return security_override
        if self.noone_home():
            return "Armed Away"
        if self.get_common().is_sleep():
            return "Armed Sleep"
        return "Armed Home"
