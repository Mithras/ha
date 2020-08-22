import globals
from random import randint


DOMAIN = "appdaemon_lock"
EVENT = f"{DOMAIN}_rotate"
ACCESS_CONTROL_MAP = {
    "0": "*{name}* has been cleared.",
    "1": "*{name}* has been locked manually.",
    "2": "*{name}* has been unlocked manually.",
    "5": "*{name}* has been locked with keypad.",
    "6": "*{name}* has been unlocked with keypad.",
    "9": "*{name}* has been locked automatically.",
    "11": "*{name}* has been jammed.",
    "16": "*{name}* keypad has been disabled.",
    "18": "*{name}* new program code has been entered."
}


class Lock(globals.Hass):
    async def initialize(self):
        config = self.args["config"]
        self._name = config["name"]
        state = config["state"]
        self._state = f"{DOMAIN}.{state}"
        self._code_slot = config["code_slot"]
        self._lock = config["lock"]
        access_control_sensor = config["access_control_sensor"]
        user_code_sensor = config["user_code_sensor"]

        await self.listen_state(self._access_control_callback_async,
                                entity=access_control_sensor)
        await self.listen_state(self._user_code_callback_async,
                                entity=user_code_sensor)
        await self.listen_event(self._event_callback_async,
                                event=EVENT,
                                state=state)

    async def _access_control_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        message = ACCESS_CONTROL_MAP.get(
            new, f"*{{name}}*: access_control - {new}.")
        await self.common.send_debug_async(message.format(name=self._name))

    async def _user_code_callback_async(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        if new == self._code_slot:
            await self._rotate_usercode_async()

    async def _event_callback_async(self, event_name, data, kwargs):
        await self._rotate_usercode_async()

    async def _rotate_usercode_async(self):
        usercode = str(randint(0, 9999)).zfill(4)
        await self.call_service("ozw/set_usercode",
                                entity_id=self._lock,
                                code_slot=self._code_slot,
                                usercode=usercode)
        await self.set_state(self._state,
                             state=usercode)
        await self.common.send_debug_async(f"*User Code #{self._code_slot}* has been changed.")
