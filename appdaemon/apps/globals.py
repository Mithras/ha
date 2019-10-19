import appdaemon.plugins.hass.hassapi as hass


class Hass(hass.Hass):
    def __init__(self, ad, name, logger, error, args, config, app_config, global_vars):
        hass.Hass.__init__(self, ad, name, logger, error, args,
                           config, app_config, global_vars)
        self.common = self.get_app("Common")
        if self.common is None:
            raise TypeError
        self.register_constraint("constrain_arm")

    def constrain_arm(self, value=None):
        arm = self.get_state(entity="appdaemon.security")
        return arm != "Disarmed" if value is None else arm in value
