import globals


# TODO: replace  "on" with a parameter. Add person == "home" triggers.
class Light(globals.Hass):
    def initialize(self):
        for config in self.args["config"]:
            instance = {}
            for sensor in config["sensors"]:
                entity = sensor["entity"]
                instance[entity] = {
                    "state": None,
                    "timer": None
                }
                self.listen_state(self.sensor_callback,
                                  instance=instance,
                                  entity=entity,
                                  additional_delay=sensor.get(
                                      "additional_delay", None),
                                  light_group=config["light_group"],
                                  sun_up_on_profile=config.get(
                                      "sun_up_on_profile", None),
                                  sun_down_on_profile=config.get(
                                      "sun_down_on_profile", None),
                                  sleep_on_profile=config.get(
                                      "sleep_on_profile", None),
                                  sun_up_off_profile=config.get(
                                      "sun_up_off_profile", None),
                                  sun_down_off_profile=config.get(
                                      "sun_down_off_profile", None),
                                  sleep_off_profile=config.get(
                                      "sleep_off_profile", None),
                                  ignore_sleep=config.get("ignore_sleep", False))

    def sensor_callback(self, entity, attribute, old, new, kwargs):
        if old != new:
            instance = kwargs["instance"]
            sensor = instance[entity]

            if new == "on":
                self.handle_on(sensor, kwargs)
            else:
                additional_delay = kwargs["additional_delay"]
                if additional_delay:
                    sensor["timer"] = self.run_in(self.timer_callback, additional_delay,
                                                  instance=instance,
                                                  sensor=sensor,
                                                  kwargs=kwargs)
                else:
                    self.handle_off(instance, sensor, kwargs)

    def timer_callback(self, kwargs):
        self.handle_off(kwargs["instance"], kwargs["sensor"], kwargs["kwargs"])

    def handle_on(self, sensor, kwargs):
        # TODO: do nothing in case currentState == offState.
        self.cancel_timer(sensor["timer"])
        sensor["state"] = True

        profile = self.get_on_profile(kwargs)
        self.handle_profile(kwargs["light_group"], profile)

    def handle_off(self, instance, sensor, kwargs):
        sensor["state"] = False
        if all(not sensor["state"] for sensor in instance.values()):
            profile = self.get_off_profile(kwargs)
            self.handle_profile(kwargs["light_group"], profile)

    def get_on_profile(self, kwargs):
        if not kwargs["ignore_sleep"] and self.common.is_sleep():
            return kwargs["sleep_on_profile"]
        elif self.sun_up():
            return kwargs["sun_up_on_profile"]
        else:
            return kwargs["sun_down_on_profile"]

    def get_off_profile(self, kwargs):
        if not kwargs["ignore_sleep"] and self.common.is_sleep():
            return kwargs["sleep_off_profile"]
        elif self.sun_up():
            return kwargs["sun_up_off_profile"]
        else:
            return kwargs["sun_down_off_profile"]

    def handle_profile(self, light_group, profile):
        if profile == "Off":
            self.common.light_turn_off(light_group)
        elif profile is not None:
            self.common.light_turn_profile(light_group, profile)
