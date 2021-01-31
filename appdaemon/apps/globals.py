import hassapi as hass
from inspect import iscoroutinefunction
from appdaemon import utils, threading
import asyncio


async def check_constraint(self, key, value, app):
    unconstrained = True
    if key in app.list_constraints():
        method = getattr(app, key)
        if(iscoroutinefunction(method)):
            unconstrained = await method(value)
        else:
            unconstrained = await utils.run_in_executor(self, method, value)
    return unconstrained

# BUG: https://github.com/home-assistant/appdaemon/issues/922
# https://github.com/AppDaemon/appdaemon/blob/master/appdaemon/threading.py
threading.Threading.check_constraint = check_constraint


class Hass(hass.Hass):
    def __init__(self, ad, name, logging, args, config, app_config, global_vars):
        hass.Hass.__init__(self, ad, name, logging, args,
                           config, app_config, global_vars)

        self._setup_task = self.create_task(self._setup())

        self.register_constraint("constrain_arm")
        self.register_constraint("constrain_enabled")
        self.app_config[self.name]["constrain_enabled"] = None

    async def initialize(self):
        await (await self._setup_task)

    # BUG: https://github.com/home-assistant/appdaemon/issues/921
    # https://github.com/AppDaemon/appdaemon/blob/master/appdaemon/adapi.py
    # def create_task(self, coro):
    #     task = asyncio.create_task(coro)
    #     self.AD.futures.add_future(self.name, task)
    #     return task

    # BUG: https://github.com/home-assistant/appdaemon/issues/926
    # https://github.com/AppDaemon/appdaemon/blob/master/appdaemon/adapi.py
    async def sun_up(self):
        return await self.now_is_between("sunrise", "sunset")

    # BUG: https://github.com/home-assistant/appdaemon/issues/926
    # https://github.com/AppDaemon/appdaemon/blob/master/appdaemon/adapi.py
    async def sun_down(self):
        return await self.now_is_between("sunset", "sunrise")

    async def constrain_arm(self, value=None):
        await self._setup_task
        arm = await self.get_state("appdaemon.security")
        return arm != "Disarmed" if value is None else arm is not None and arm in value

    async def constrain_enabled(self, value):
        await self._setup_task
        state = await self.get_state(self._app_state_name)
        return state == "on"

    async def _setup(self):
        friendly_name_list = [self.name[0]]
        state_list = [*"appdaemon_app.", self.name[0].lower()]
        for x in self.name[1:]:
            if x.isupper():
                friendly_name_list.append(" ")
                state_list.append("_")
            friendly_name_list.append(x)
            state_list.append(x.lower())

        app_friendly_name = "".join(friendly_name_list)
        self._app_state_name = "".join(state_list)

        if await self.get_state(self._app_state_name) is None:
            await self.set_state(self._app_state_name,
                                 state="on",
                                 attributes={"friendly_name": app_friendly_name})

        self.common = await self.get_app("Common")
