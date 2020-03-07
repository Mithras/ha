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
threading.Threading.check_constraint = check_constraint


class Hass(hass.Hass):
    def __init__(self, ad, name, logging, args, config, app_config, global_vars):
        hass.Hass.__init__(self, ad, name, logging, args,
                           config, app_config, global_vars)

        self.setup_app_state()

        self.register_constraint("constrain_arm")
        self.register_constraint("constrain_enabled")
        self.app_config[self.name]["constrain_enabled"] = None

    def get_common(self):
        return self.get_app("Common")

    def constrain_arm(self, value=None):
        arm = self.get_state("appdaemon.security")
        return arm != "Disarmed" if value is None else arm in value

    def constrain_enabled(self, value):
        state = self.get_state(self.__app_state_name)
        return state == "on"

    def setup_app_state(self):
        friendly_name_list = [self.name[0]]
        state_list = [*"appdaemon_app.", self.name[0].lower()]
        for x in self.name[1:]:
            if x.isupper():
                friendly_name_list.append(" ")
                state_list.append("_")
            friendly_name_list.append(x)
            state_list.append(x.lower())

        app_friendly_name = "".join(friendly_name_list)
        self.__app_state_name = "".join(state_list)

        if self.get_state(self.__app_state_name) is None:
            self.set_state(self.__app_state_name,
                           state="on",
                           attributes={"friendly_name": app_friendly_name})

    # https://github.com/home-assistant/appdaemon/issues/921
    def create_task(self, coro, **kwargs):
        task = asyncio.create_task(coro)
        self.AD.futures.add_future(self.name, task)
        return task


class HassAsync(hass.Hass):
    def __init__(self, ad, name, logging, args, config, app_config, global_vars):
        hass.Hass.__init__(self, ad, name, logging, args,
                           config, app_config, global_vars)

        self.__setup_task = self.create_task(self.__setup())

        self.register_constraint("constrain_arm")
        self.register_constraint("constrain_enabled")
        self.app_config[self.name]["constrain_enabled"] = None

    # BUG: https://github.com/home-assistant/appdaemon/issues/921
    def create_task(self, coro, **kwargs):
        task = asyncio.create_task(coro)
        self.AD.futures.add_future(self.name, task)
        return task

    async def constrain_arm(self, value=None):
        await self.__setup_task
        arm = await self.get_state("appdaemon.security")
        return arm != "Disarmed" if value is None else arm in value

    async def constrain_enabled(self, value):
        await self.__setup_task
        state = await self.get_state(self.__app_state_name)
        return state == "on"

    async def __setup(self):
        friendly_name_list = [self.name[0]]
        state_list = [*"appdaemon_app.", self.name[0].lower()]
        for x in self.name[1:]:
            if x.isupper():
                friendly_name_list.append(" ")
                state_list.append("_")
            friendly_name_list.append(x)
            state_list.append(x.lower())

        app_friendly_name = "".join(friendly_name_list)
        self.__app_state_name = "".join(state_list)

        if await self.get_state(self.__app_state_name) is None:
            await self.set_state(self.__app_state_name,
                                 state="on",
                                 attributes={"friendly_name": app_friendly_name})

        self.common = await self.get_app("Common")
