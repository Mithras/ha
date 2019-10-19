import globals

EVENT_CODE_DESCRIPTION_MAP = {
    "x000": "Initial Press",
    "x001": "Hold",
    "x002": "Release(after press)",
    "x003": "Release(after hold)",
    "x004": "Double press",
    "x005": "Triple press",
    "x006": "Quadruple press",
    "x007": "Shake",
    "x008": "Drop",
    "x009": "Tilt",
    "x010": "Many press"
}


class DeconzSwitch(globals.Hass):
    def initialize(self):
        for entity in self.args["config"]:
            self.listen_event(self.callback,
                              event="deconz_event",
                              id=entity)

    def callback(self, event_name, data, kwargs):
        entity = data["id"]
        deconz_event = str(data["event"])
        button = int(deconz_event[0])
        code = f"x{deconz_event[1:]}"
        description = EVENT_CODE_DESCRIPTION_MAP.get(code, "Unknown")
        self.fire_event("deconz_event_custom",
                        entity_id=entity,
                        deconz_event=deconz_event,
                        button=button,
                        code=code,
                        description=description)
