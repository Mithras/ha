import globals


class LivingRoom(globals.Hass):
    def initialize(self):
        config = self.args["config"]
        self.mithras_desktop = config["mithras_desktop"]
        self.wyrd_and_jotunheim = config["wyrd_and_jotunheim"]
        self.rokit6 = config["rokit6"]
        self.samsung_tv = config["samsung_tv"]
        self.levoit_humidifier = config["levoit_humidifier"]
        self.living_room_main_light = config["living_room_main_light"]
        self.living_room_back_light = config["living_room_back_light"]
        self.light_strip = config["light_strip"]

        self.listen_state(self.mithras_desktop_callback,
                          entity=self.mithras_desktop)
        self.listen_state(self.person_home_callback,
                          entity=config["person"],
                          new="home")
        self.listen_state(self.person_not_home_callback,
                          entity=config["person"],
                          new="not_home")
        self.listen_state(self.awake_callback,
                          entity=config["sleep_input"],
                          new="off")

    def mithras_desktop_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        if new == "on":
            self.activate()
        else:
            self.deactivate()

    def person_home_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        self.activate(toggle=False)
        self.turn_on(self.mithras_desktop)

    def person_not_home_callback(self, entity, attribute, old, new, kwargs):
        if old == new or self.anyone_home:
            return
        toggle = self.get_state(self.mithras_desktop) == "on"
        self.deactivate(toggle=toggle)

    def awake_callback(self, entity, attribute, old, new, kwargs):
        if old == new:
            return
        self.turn_on(self.mithras_desktop)

    def activate(self, **kwargs):
        toggle = kwargs.get("toggle", True)
        self.turn_on(self.wyrd_and_jotunheim)
        self.turn_on(self.rokit6)
        self.turn_on(self.samsung_tv)
        self.get_common().light_turn_bright(self.living_room_main_light)
        self.get_common().light_turn_dimmed(self.living_room_back_light)
        if toggle:
            self.toggle(self.levoit_humidifier)

    def deactivate(self, **kwargs):
        toggle = kwargs.get("toggle", True)
        self.turn_off(self.wyrd_and_jotunheim)
        self.turn_off(self.rokit6)
        self.turn_off(self.samsung_tv)
        self.get_common().light_turn_off(self.living_room_main_light)
        self.get_common().light_turn_off(self.living_room_back_light)
        self.get_common().light_turn_off(self.light_strip)
        if toggle:
            self.toggle(self.levoit_humidifier)
