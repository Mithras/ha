import globals


# TODO: replace  "on" with a parameter. Add person == "home" triggers.
class Light(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.light_group = config["light_group"]
        self.sun_up_on_profile = config.get("sun_up_on_profile", None)
        self.sun_down_on_profile = config.get("sun_down_on_profile", None)
        self.sleep_on_profile = config.get("sleep_on_profile", None)
        self.sun_up_off_profile = config.get("sun_up_off_profile", None)
        self.sun_down_off_profile = config.get("sun_down_off_profile", None)
        self.sleep_off_profile = config.get("sleep_off_profile", None)
        self.ignore_sleep = config.get("ignore_sleep", False)
        self.sensorMap = {}

        for sensor in config["sensors"]:
            entity = sensor["entity"]
            self.sensorMap[entity] = {
                "state": None,
                "timer": None
            }
            self.listen_state(self.sensor_callback,
                              entity=entity,
                              additional_delay=sensor.get("additional_delay", None))

    def sensor_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        sensor = self.sensorMap[entity]

        if new == "on":
            self.handle_on(sensor)
        else:
            additional_delay = kwargs["additional_delay"]
            if additional_delay:
                sensor["timer"] = self.run_in(self.timer_callback, additional_delay,
                                              sensor=sensor)
            else:
                self.handle_off(sensor)

    def timer_callback(self, kwargs):
        self.handle_off(kwargs["sensor"])

    def handle_on(self, sensor):
        self.cancel_timer(sensor["timer"])
        sensor["state"] = True
        on_profile = self.get_on_profile()
        self.handle_profile(self.light_group, on_profile)

    def handle_off(self, sensor):
        sensor["state"] = False
        if all(not sensor["state"] for sensor in self.sensorMap.values()):
            off_profile = self.get_off_profile()
            self.handle_profile(self.light_group, off_profile)

    def get_on_profile(self):
        if not self.ignore_sleep and self.common.is_sleep():
            return self.sleep_on_profile
        elif self.sun_up():
            return self.sun_up_on_profile
        else:
            return self.sun_down_on_profile

    def get_off_profile(self):
        if not self.ignore_sleep and self.common.is_sleep():
            return self.sleep_off_profile
        elif self.sun_up():
            return self.sun_up_off_profile
        else:
            return self.sun_down_off_profile

    def handle_profile(self, light_group, profile):
        if profile == "Off":
            self.common.light_turn_off(light_group)
        elif profile is not None:
            self.common.light_turn_profile(light_group, profile)
