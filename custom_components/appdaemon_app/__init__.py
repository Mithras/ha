from homeassistant.const import (
    STATE_ON, STATE_OFF, SERVICE_TURN_ON, SERVICE_TURN_OFF, SERVICE_TOGGLE, ATTR_ENTITY_ID)


DOMAIN = 'appdaemon_app'


def setup(hass, config):
    def turn_on(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        state_obj = hass.states.get(entity_id)
        hass.states.set(entity_id, STATE_ON, state_obj.attributes)

    def turn_off(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        state_obj = hass.states.get(entity_id)
        hass.states.set(entity_id, STATE_OFF, state_obj.attributes)

    def toggle(call):
        entity_id = call.data[ATTR_ENTITY_ID]
        state_obj = hass.states.get(entity_id)
        hass.states.set(entity_id,
                        STATE_ON if state_obj.state == STATE_OFF else STATE_OFF,
                        state_obj.attributes)

    def fire_event(call):
        event = call.data["event"]
        hass.bus.fire(event, call.data)

    hass.services.register(DOMAIN, SERVICE_TURN_ON, turn_on)
    hass.services.register(DOMAIN, SERVICE_TURN_OFF, turn_off)
    hass.services.register(DOMAIN, SERVICE_TOGGLE, toggle)
    hass.services.register(
        DOMAIN, "fire_event", fire_event)

    return True
