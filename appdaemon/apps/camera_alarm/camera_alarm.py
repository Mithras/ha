import globals
import string
import random
from datetime import datetime


SYMBOLS = string.ascii_lowercase + string.digits
MAX_RETRY = 10


class CameraAlarm(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self._camera = config["camera"]
        self._video_duration = config["video_duration"]
        self._camera_output_dir = config["camera_output_dir"]
        self._sensorStateMap = {}
        self._record_timer = None
        for entity in config["sensors"]:
            self._sensorStateMap[entity] = self.get_state(entity=entity)
            self.listen_state(self._sensor_callback,
                              entity=entity)

    def _sensor_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        self._sensorStateMap[entity] = new

        if new == "on":
            self.run_in(
                self._snapshot_timer_callback, 0)
            if not self._record_timer:
                self._record()

    def _snapshot_timer_callback(self, kwargs):
        name = self._get_name()
        filename = f"{self._camera_output_dir}/{name}.jpg"

        self.call_service("camera/snapshot",
                          entity_id=self._camera,
                          filename=filename)
        self.call_service("telegram_bot/send_photo",
                          target=[self.common.telegram_alarm_chat],
                          file=filename)

    def _record(self, retry=0):
        if all(state == "off" for state in self._sensorStateMap.values()):
            self.cancel_timer(self._record_timer)
            self._record_timer = None
            return

        name = self._get_name()
        filename = f"{self._camera_output_dir}/{name}.mp4"
        try:
            self.call_service("camera/record",
                              entity_id=self._camera,
                              filename=filename,
                              duration=self._video_duration)
            self._record_timer = self.run_in(
                self._record_timer_callback, self._video_duration + 1, retry=0)
        except:
            if retry == MAX_RETRY:
                self._record_timer = None
                raise
            self._record_timer = self.run_in(
                self._record_timer_callback, 1, retry=retry + 1)

    def _record_timer_callback(self, kwargs):
        self._record(kwargs["retry"])

    def _get_name(self):
        now = datetime.now()
        random_string = self._random_string(10)
        return now.strftime(
            f"[{self._camera}][%Y-%m-%d][%H-%M-%S].{random_string}")

    def _random_string(self, length: int):
        return "".join(random.choice(SYMBOLS) for i in range(length))
