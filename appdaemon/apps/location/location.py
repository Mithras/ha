import globals


class Location(globals.Hass):
    def initialize(self):
        self.listen_state(self.state_callback)

    def state_callback(self, entity, attribute, old, new, kwargs):
        if not entity.startswith("person.") or old == new:
            return
        if new == "not_home":
            self.get_common().send_location(entity,
                                            f"*{self.friendly_name(entity)}* has left *{old}*.")
        else:
            self.get_common().send_location(entity,
                                            f"*{self.friendly_name(entity)}* is at *{new}*.")
