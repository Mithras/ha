import globals
import string
import random
from datetime import datetime


SYMBOLS = string.ascii_lowercase + string.digits
MAX_RETRY = 10


class CameraAlarm(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._camera = config["camera"]
        self._video_duration = config["video_duration"]
        self._camera_output_dir = config["camera_output_dir"]
        self._sensorStateMap = {}
        self._record_task = None
        for entity in config["sensors"]:
            self._sensorStateMap[entity] = await self.get_state(entity)
            await self.listen_state(self._sensor_callback_async,
                                    entity=entity)

    async def _sensor_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        self._sensorStateMap[entity] = new

        if new == "on":
            send_snapshot_task = self.create_task(self._send_snapshot_async())
            if not self._record_task:
                self._record_task = self.create_task(self._record_async())
                await self._record_task
            await send_snapshot_task

    async def _send_snapshot_async(self):
        name = self._get_name()
        filename = f"{self._camera_output_dir}/{name}.jpg"

        await self.call_service("camera/snapshot",
                                entity_id=self._camera,
                                filename=filename)
        await self.call_service("telegram_bot/send_photo",
                                target=[self.common.telegram_alarm_chat],
                                file=filename)

    async def _record_async(self):
        retry = 0
        while any(state == "on" for state in self._sensorStateMap.values()):
            try:
                name = self._get_name()
                filename = f"{self._camera_output_dir}/{name}.mp4"
                result = await self.call_service("camera/record",
                                                 entity_id=self._camera,
                                                 filename=filename,
                                                 duration=self._video_duration)
                if result is None:
                    raise Exception(
                        "call_service() swallows exceptions and returns None")
                retry = 0
                await self.sleep(self._video_duration + 1)
            except:
                if retry == MAX_RETRY:
                    self._record_task = None
                    raise
                retry += 1
                await self.sleep(1)

        self._record_task = None

    def _get_name(self):
        now = datetime.now()
        random_string = self._random_string(10)
        return now.strftime(
            f"[{self._camera}][%Y-%m-%d][%H-%M-%S].{random_string}")

    def _random_string(self, length: int):
        return "".join(random.choice(SYMBOLS) for i in range(length))
