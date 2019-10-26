import globals


class LivingRoomCube(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        unique_id = config["unique_id"]
        self.listen_event(self.flip_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="flip")
        self.listen_event(self.rotate_left_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="rotate_left")
        self.listen_event(self.rotate_right_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="rotate_right")
        self.listen_event(self.knock_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="knock")
        self.listen_event(self.drop_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="drop")
        self.listen_event(self.slide_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="slide")
        self.listen_event(self.shake_callback,
                          event="zha_event",
                          unique_id=unique_id,
                          command="shake")
        # self.log(f"light.hallway: {self.common.get_profile('light.hallway')}")
        # self.log(f"light.kitchen: {self.common.get_profile('light.kitchen')}")

    def flip_callback(self, event_name, data, kwargs):
        if data["args"]["flip_degrees"] == 90:
            self.flip_90_callback(event_name, data, kwargs)
        else:
            self.flip_180_callback(event_name, data, kwargs)

    def flip_90_callback(self, event_name, data, kwargs):
        self.log(f"flip_90_callback: {data}")
        # TODO: kitchen light: lower -> upper -> both -> off

    def flip_180_callback(self, event_name, data, kwargs):
        self.log(f"flip_180_callback: {data}")
        # TODO: kitchen light app: on/off

    def rotate_left_callback(self, event_name, data, kwargs):
        self.log(f"rotate_left_callback: {data}")
        # TODO: living room light: bright/bright -> bright/dimmed -> dimmed/nightlight -> nightlight/off

    def rotate_right_callback(self, event_name, data, kwargs):
        self.log(f"rotate_right_callback: {data}")
        # TODO: living room light: reverse

    def knock_callback(self, event_name, data, kwargs):
        self.log(f"knock_callback: {data}")
        # TODO: living room light: on/off

    def drop_callback(self, event_name, data, kwargs):
        self.log(f"drop_callback: {data}")

    def slide_callback(self, event_name, data, kwargs):
        self.log(f"slide_callback: {data}")

    def shake_callback(self, event_name, data, kwargs):
        self.log(f"shake_callback: {data}")
        # TODO: fireplace on/off
