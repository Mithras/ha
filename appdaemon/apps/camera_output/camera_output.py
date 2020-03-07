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


File = namedtuple(
    "File", ["file_name", "file_path", "external_path", "ext", "size"])


class DirState():
    def __init__(self, app, dir, external_path):
        self._app = app
        self._dir = dir
        self._external_path = external_path

        self.count = 0
        self.size = 0
        self.files = []

    def add_file(self, file_name):
        file_path = join(self._dir, file_name)
        external_path = f"{self._external_path}/{file_name}"
        _, ext = splitext(file_name)
        size = stat(file_path).st_size

        file = File(file_name, file_path, external_path, ext, size)

        self.files.append(file)
        self.count += 1
        self.size += size
        self._app.run_in(self.__update_size_callback, FILE_SIZE_DELAY,
                         file=file,
                         index=len(self.files) - 1)

    def __update_size_callback(self, kwargs):
        file = kwargs["file"]
        index = kwargs["index"]

        file_name, file_path, external_path, ext, size = file
        new_size = stat(file_path).st_size
        if(new_size == size):
            return

        new_file = File(file_name, file_path, external_path, ext, new_size)
        self.files[index] = new_file
        self.size -= size
        self.size += new_file.size


class CameraOutput(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self._dir = config["camera_output_dir"]
        self._external_path = config["camera_output_external_path"]

        self._reload()
        self.listen_event(self._created_event_callback,
                          event="folder_watcher",
                          event_type="created",
                          folder=self._dir)
        self.listen_event(self._clear_event_callback,
                          event=CLEAR_EVENT)

    def _reload(self):
        self.dir_state = DirState(self, self._dir, self._external_path)
        for file in sorted(listdir(self._dir)):
            self.dir_state.add_file(file)
        self._update_state()

    def _update_state(self):
        snapshots = []
        videos = []
        for stats in reversed(self.dir_state.files):
            if stats.ext == ".jpg" and len(snapshots) < SNAPSHOT_COUNT:
                snapshots.append(stats.external_path)
            if stats.ext == ".mp4" and len(videos) < VIDEO_COUNT:
                videos.append(stats.external_path)
            if len(snapshots) == SNAPSHOT_COUNT and len(videos) == VIDEO_COUNT:
                break

        self.set_state(STATE,
                       state="on",
                       attributes={
                           "count": self.dir_state.count,
                           "size": self.dir_state.size,
                           "snapshots": json.dumps(snapshots),
                           "videos": json.dumps(videos)
                       })

    def _created_event_callback(self, event_name, data, kwargs):
        self.dir_state.add_file(data["file"])
        self._update_state()

    def _clear_event_callback(self, event_name, data, kwargs):
        for file in listdir(self._dir):
            file_path = join(self._dir, file)
            remove(file_path)
        self._reload()
