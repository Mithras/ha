import globals
from random import randint


class Lock(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.lock_name = config["lock_name"]
        self.lock_node_id = config["lock_node_id"]
        self.alarm_type = config["alarm_type"]
        self.alarm_level = config["alarm_level"]
        self.lock_entity = config["lock_entity"]
        self.access_control_sensor = config["access_control_sensor"]
        self.alarm_type_sensor = config["alarm_type_sensor"]
        self.alarm_level_sensor = config["alarm_level_sensor"]

        self.listen_state(self.lock_state_callback,
                          entity=self.access_control_sensor)

    def access_control_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        lock_status = self.get_state(
            entity=self.lock_entity,
            attribute="lock_status")
        self.common.send_debug(
            f"*{self.lock_name}* has been {lock_status.lower()}.")

        alarm_type = int(self.get_state(
            entity=self.alarm_type_sensor))
        alarm_level = int(self.get_state(
            entity=self.alarm_level_sensor))
        if alarm_type != self.alarm_type or alarm_level != self.alarm_level:
            return

        usercode = str(randint(0, 9999)).zfill(4)
        self.call_service("lock/set_usercode",
                          node_id=self.lock_node_id,
                          code_slot=alarm_level,
                          usercode=usercode)
        self.common.send_debug(f"*User Code #{alarm_level}* has been changed.")
