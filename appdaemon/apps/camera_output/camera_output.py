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


File = namedtuple(
    "File", ["file", "file_path", "external_path", "ext", "size"])


class DirState():
    def __init__(self, dir, external_path):
        self._dir = dir
        self._external_path = external_path

        self.count = 0
        self.size = 0
        self.files = []

    def add_file(self, file):
        file_path = join(self._dir, file)
        external_path = f"{self._external_path}/{file}"
        _, ext = splitext(file)
        size = stat(file_path).st_size

        self.files.append(File(file, file_path, external_path, ext, size))
        self.count += 1
        self.size += size


class CameraOutput(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self._dir = config["camera_output_dir"]
        self._external_path = config["camera_output_external_path"]

        self.common.run_async(self._reload)
        self.listen_event(self._created_event_callback,
                          event="folder_watcher",
                          event_type="created",
                          folder=self._dir)
        self.listen_event(self._clear_event_callback,
                          event=CLEAR_EVENT)

    def _reload(self):
        self.dir_state = DirState(self._dir, self._external_path)
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

        self.common.run_async(self.set_state,
                              STATE,
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
