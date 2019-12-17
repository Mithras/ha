import globals


class SensorAlarm(globals.Hass):
    def initialize(self):
        for entity in self.args["config"]:
            self.listen_state(self.callback,
                              entity=entity)

    def callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        device_type = self.get_state(
            entity=entity, attribute="device_class")
        if device_type == "opening":
            self.common.send_alarm(
                f"*{self.friendly_name(entity)}* has {'opened' if new=='on' else 'closed'}.")
        elif device_type == "motion":
            if new == "on":
                self.common.send_alarm(
                    f"*{self.friendly_name(entity)}* has detected motion.")
        elif device_type == "connectivity":
            self.common.send_alarm(
                f"*{self.friendly_name(entity)}* has {'connected' if new=='on' else 'disconnected'}.")
        else:
            self.common.send_alarm(
                f"*{self.friendly_name(entity)}* is in {new} state.")
