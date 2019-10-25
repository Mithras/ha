import globals


class Location(globals.Hass):
    def initialize(self):
        self.listen_state(self.state_callback)

    def state_callback(self, entity, attribute, old, new, kwargs):
        if not entity.startswith("person.") or old == new:
            return
        if new == "not_home":
            self.common.send_location(
                f"*{self.friendly_name(entity)}* has left *{old}*.")
        else:
            self.common.send_location(
                f"*{self.friendly_name(entity)}* is at *{new}*.")
