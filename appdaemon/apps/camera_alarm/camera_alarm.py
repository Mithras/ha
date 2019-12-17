import globals
import string
import random
from datetime import date


SYMBOLS = string.ascii_lowercase + string.digits
OUTPUT_DIR = f"/config/www/camera"


class CameraAlarm(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self._camera = config["camera"]
        self._video_duration = config["video_duration"]
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
            self._send_snapshot()
            self._start_recording()
        else:
            self._stop_recording()

    def _send_snapshot(self):
        name = self._get_name()
        filename = f"{OUTPUT_DIR}/{name}.jpg"

        self.call_service("camera/snapshot",
                          entity_id=self._camera,
                          filename=filename)
        self.call_service("telegram_bot/send_photo",
                          target=[self.common.telegram_alarm_chat],
                          file=filename)

    def _start_recording(self):
        if self._record_timer:
            return
        self._record()

    def _stop_recording(self):
        if all(state == "off" for state in self._sensorStateMap.values()):
            self.cancel_timer(self._record_timer)
            self._record_timer = None

    def _record(self):
        name = self._get_name()
        filename = f"{OUTPUT_DIR}/{name}.mp4"
        self.call_service("camera/record",
                          entity_id=self._camera,
                          filename=filename,
                          duration=self._video_duration)
        self._record_timer = self.run_in(
            self._record_timer_callback, self._video_duration)

    def _record_timer_callback(self, kwargs):
        self._record()

    def _get_name(self):
        today = date.today()
        random_string = self._random_string(10)
        return today.strftime(
            f"[{self._camera}][%Y-%m-%d][%H-%M-%S].{random_string}")

    def _random_string(self, length: int):
        return "".join(random.choice(SYMBOLS) for i in range(length))
