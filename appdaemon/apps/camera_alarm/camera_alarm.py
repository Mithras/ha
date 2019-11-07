import globals
import string
import random


SYMBOLS = string.ascii_lowercase + string.digits


# TODO: support multiple sensors per camera
# TODO: write videos until sensor(s) are clear
class CameraAlarm(globals.Hass):
    def initialize(self):
        for config in self.args["config"]:
            self.listen_state(self.sensor_callback,
                              entity=config["sensor"],
                              new="on",
                              camera=config["camera"],
                              video_duration=config["video_duration"],
                              send_video_delay=config["send_video_delay"])

    def sensor_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        camera = kwargs["camera"]
        video_duration = kwargs["video_duration"]
        send_video_delay = kwargs["send_video_delay"]
        last_updated = self.convert_utc(self.get_state(
            entity=entity,
            attribute="last_updated"))
        random_string = self.random_string(10)
        name = last_updated.strftime(
            f"[{camera}][%Y-%m-%d][%H-%M-%S].{random_string}")
        snapshot = f"/config/www/camera/{name}.jpg"
        video = f"/config/www/camera/{name}.mp4"
        # snapshot_public_url = f"{self.common.http_base_url}/local/camera/{self.common.escapeMarkdown(name)}.jpg"
        video_public_url = f"{self.common.http_base_url}/local/camera/{self.common.escapeMarkdown(name)}.mp4"

        self.call_service("camera/snapshot",
                          entity_id=camera,
                          filename=snapshot)
        self.call_service("camera/record",
                          entity_id=camera,
                          filename=video,
                          duration=video_duration)

        self.call_service("telegram_bot/send_photo",
                          target=[self.common.telegram_alarm_chat],
                          file=snapshot)
        # self.common.send_alarm(snapshot_public_url)
        self.run_in(self.timer_callback, send_video_delay,
                    video_public_url=video_public_url)

    def timer_callback(self, kwargs):
        video_public_url = kwargs["video_public_url"]
        self.common.send_alarm(video_public_url)

    def random_string(self, length: int):
        return "".join(random.choice(SYMBOLS) for i in range(length))
