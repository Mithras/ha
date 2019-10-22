import globals


# TODO: do nothing in case currentState == offState.
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
                                  sun_up_on_scene=config.get(
                                      "sun_up_on_scene", None),
                                  sun_down_on_scene=config.get(
                                      "sun_down_on_scene", None),
                                  sleep_on_scene=config.get(
                                      "sleep_on_scene", None),
                                  sun_up_off_scene=config.get(
                                      "sun_up_off_scene", None),
                                  sun_down_off_scene=config.get(
                                      "sun_down_off_scene", None),
                                  sleep_off_scene=config.get(
                                      "sleep_off_scene", None),
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
        self.cancel_timer(sensor["timer"])
        sensor["state"] = True

        if not kwargs["ignore_sleep"] and self.common.is_sleep():
            scene = kwargs["sleep_on_scene"]
        elif self.sun_up():
            scene = kwargs["sun_up_on_scene"]
        else:
            scene = kwargs["sun_down_on_scene"]
        self.handle_scene(kwargs["light_group"], scene)

    def handle_off(self, instance, sensor, kwargs):
        sensor["state"] = False
        if all(not sensor["state"] for sensor in instance.values()):
            if not kwargs["ignore_sleep"] and self.common.is_sleep():
                scene = kwargs["sleep_off_scene"]
            elif self.sun_up():
                scene = kwargs["sun_up_off_scene"]
            else:
                scene = kwargs["sun_down_off_scene"]
            self.handle_scene(kwargs["light_group"], scene)

    def handle_scene(self, light_group, scene):
        if scene == "Off":
            self.common.light_turn_off(light_group)
        elif scene is not None:
            self.common.light_turn_profile(light_group, scene)
