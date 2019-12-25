import globals


push = ("1000", "2000", "3000", "4000", "5000", "6000")
double_tap = ("1001", "2002", "3003", "4004", "5005", "6006")
flip_180 = ("1006", "2005", "3004", "4003", "5002", "6001")
flip_90 = ("1002", "1003", "1004", "1005", "2001", "2003", "2004", "2006", "3001", "3002", "3005",
           "3006", "4001", "4002", "4005", "4006", "5001", "5003", "5004", "5006", "6002", "6003", "6004", "6005")
shake = ("7007")
drop = ("7008")
wake = ("7000")


class DeconzCube(globals.Hass):
    def initialize(self):
        for config in self.args["config"]:
            unique_id = config["unique_id"]
            digital_id = config["digital_id"]
            analog_id = config["analog_id"]
            self.listen_event(self.digital_callback,
                              event="deconz_event",
                              unique_id=unique_id,
                              id=digital_id)
            self.listen_event(self.analog_callback,
                              event="deconz_event",
                              unique_id=unique_id,
                              id=analog_id)

    def digital_callback(self, event_name, data, kwargs):
        unique_id = data["unique_id"]
        deconz_event = str(data["event"])

        if deconz_event in push:
            return self.fire_deconz_event(unique_id, "push")
        if deconz_event in double_tap:
            return self.fire_deconz_event(unique_id, "double_tap")
        if deconz_event in flip_180:
            return self.fire_deconz_event(unique_id, "flip_180")
        if deconz_event in flip_90:
            return self.fire_deconz_event(unique_id, "flip_90")
        if deconz_event in shake:
            return self.fire_deconz_event(unique_id, "shake")
        if deconz_event in drop:
            return self.fire_deconz_event(unique_id, "drop")
        if deconz_event in wake:
            return self.fire_deconz_event(unique_id, "wake")

    def analog_callback(self, event_name, data, kwargs):
        unique_id = data["unique_id"]
        deconz_event = str(data["event"])

        if deconz_event[0] == "-":
            return self.fire_deconz_event(unique_id, "rotate_left")
        return self.fire_deconz_event(unique_id, "rotate_right")

    def fire_deconz_event(self, unique_id: str, command: str):
        self.common.run_async(self.fire_event,
                              "deconz_event_custom",
                              unique_id=unique_id,
                              command=command)
