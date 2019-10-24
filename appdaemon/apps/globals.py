import appdaemon.plugins.hass.hassapi as hass


class Hass(hass.Hass):
    def __init__(self, ad, name, logger, error, args, config, app_config, global_vars):
        hass.Hass.__init__(self, ad, name, logger, error, args,
                           config, app_config, global_vars)
        self.common = self.get_app("Common")
        if self.common is None:
            raise TypeError

        self.setup_app_state()

        self.register_constraint("constrain_arm")
        self.register_constraint("constrain_enabled")
        self.app_config[self.name]["constrain_enabled"] = None

    def constrain_arm(self, value=None):
        arm = self.get_state(entity="appdaemon.security")
        return arm != "Disarmed" if value is None else arm in value

    def constrain_enabled(self, value):
        state = self.get_state(entity=self.app_state_name)
        return state == "on"

    def setup_app_state(self):
        friendly_name_list = [self.name[0]]
        state_list = [*"appdaemon_app.", self.name[0].lower()]
        for x in self.name[1:]:
            if x.isupper():
                friendly_name_list.append(" ")
                state_list.append("_")
                state_list.append(x.lower())
            else:
                state_list.append(x)
            friendly_name_list.append(x)

        self.app_friendly_name = "".join(friendly_name_list)
        self.app_state_name = "".join(state_list)

        if self.get_state(entity=self.app_state_name) is None:
            self.set_state(self.app_state_name,
                           state="on",
                           attributes={"friendly_name": self.app_friendly_name})
