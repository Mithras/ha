import globals
from os import listdir, stat, remove
from os.path import join, splitext
from collections import namedtuple
import json


DOMAIN = "appdaemon_camera_output"
STATE = f"{DOMAIN}.stats"
SNAPSHOT_COUNT = 5
VIDEO_COUNT = 25
CLEAR_EVENT = f"{DOMAIN}_clear"
FILE_SIZE_DELAY = 15


File = namedtuple("File", ["file_name", "file_path",
                           "external_path", "ext", "size"])


class CameraOutput(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._dir = config["camera_output_dir"]
        self._external_path = config["camera_output_external_path"]

        await self._reload_async()
        await self.listen_event(self._created_event_callback_async,
                                event="folder_watcher",
                                event_type="created",
                                folder=self._dir)
        await self.listen_event(self._clear_event_callback_async,
                                event=CLEAR_EVENT)

    async def _created_event_callback_async(self, event_name, data, kwargs):
        index = self._add_file(data["file"])
        await self._update_state_async()
        await self.sleep(FILE_SIZE_DELAY)
        self._update_file(index)
        await self._update_state_async()

    async def _clear_event_callback_async(self, event_name, data, kwargs):
        for file in listdir(self._dir):
            file_path = join(self._dir, file)
            remove(file_path)
        await self._reload_async()

    async def _reload_async(self):
        self.count = 0
        self.size = 0
        self.files = []
        for file in sorted(listdir(self._dir)):
            self._add_file(file)
        await self._update_state_async()

    def _add_file(self, file_name):
        file_path = join(self._dir, file_name)
        external_path = f"{self._external_path}/{file_name}"
        _, ext = splitext(file_name)
        size = stat(file_path).st_size

        file = File(file_name, file_path, external_path, ext, size)

        self.files.append(file)
        self.count += 1
        self.size += size

        return len(self.files) - 1

    def _update_file(self, index):
        file_name, file_path, external_path, ext, size = self.files[index]

        new_size = stat(file_path).st_size
        if(new_size == size):
            return

        new_file = File(file_name, file_path, external_path, ext, new_size)
        self.files[index] = new_file
        self.size -= size
        self.size += new_size

    async def _update_state_async(self):
        snapshots = []
        videos = []
        for stats in reversed(self.files):
            if stats.ext == ".jpg" and len(snapshots) < SNAPSHOT_COUNT:
                snapshots.append(stats.external_path)
            if stats.ext == ".mp4" and len(videos) < VIDEO_COUNT:
                videos.append(stats.external_path)
            if len(snapshots) == SNAPSHOT_COUNT and len(videos) == VIDEO_COUNT:
                break

        await self.set_state(STATE,
                             state="on",
                             attributes={
                                 "count": self.count,
                                 "size": self.size,
                                 "snapshots": json.dumps(snapshots),
                                 "videos": json.dumps(videos)
                             })
