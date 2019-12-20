import globals
from random import randint


DOMAIN = "appdaemon_lock"
EVENT = f"{DOMAIN}_rotate"


class Lock(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self._name = config["name"]
        state = config["state"]
        self._state = f"{DOMAIN}.{state}"
        self._node_id = config["node_id"]
        self._code_slot = config["code_slot"]
        self._alarm_type = config["alarm_type"]
        self._alarm_level = config["alarm_level"]
        self._lock = config["lock"]
        self._access_control_sensor = config["access_control_sensor"]
        self._alarm_type_sensor = config["alarm_type_sensor"]
        self._alarm_level_sensor = config["alarm_level_sensor"]

        self.listen_state(self._access_control_callback,
                          entity=self._access_control_sensor)

        self.listen_event(self._event_callback,
                          event=EVENT,
                          state=state)

    def _event_callback(self, event_name, data, kwargs):
        self._rotate_usercode()

    def _access_control_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        lock_status = self.get_state(
            entity=self._lock,
            attribute="lock_status")
        self.common.send_debug(
            f"*{self._name}* has been {lock_status.lower()}.")

        alarm_type = int(self.get_state(
            entity=self._alarm_type_sensor))
        alarm_level = int(self.get_state(
            entity=self._alarm_level_sensor))
        if alarm_type == self._alarm_type and alarm_level == self._alarm_level:
            self._rotate_usercode()

    def _rotate_usercode(self):
        usercode = str(randint(0, 9999)).zfill(4)
        self.call_service("lock/set_usercode",
                          node_id=self._node_id,
                          code_slot=self._code_slot,
                          usercode=usercode)
        self.set_state(self._state,
                       state=usercode)
        self.common.send_debug(
            f"*User Code #{self._code_slot}* has been changed.")
