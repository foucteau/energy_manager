"""Initialisation du composant Energy Manager."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configurer Energy Manager."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurer l'entrée ajoutée via l'interface utilisateur."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    max_threshold = entry.data.get("max_energy_threshold")
    energy_sensor = entry.data.get("energy_sensor")
    device_list = entry.options.get("device_list", [])

    for device in device_list:
        if not device.get("power_sensor"):
            suggested_sensor = f"sensor.{device['entity_id'].split('.')[-1]}_power"
            if hass.states.get(suggested_sensor):
                device["power_sensor"] = suggested_sensor
            else:
                hass.states.async_set(f"{DOMAIN}.status", f"Error: No power sensor for {device['entity_id']}")

    async def energy_monitor(event):
        total_power = sum(
            float(hass.states.get(device["power_sensor"]).state or 0)
            for device in device_list
            if hass.states.get(device["power_sensor"])
        )
        if total_power > max_threshold:
            hass.states.async_set(f"{DOMAIN}.status", f"Over threshold: {total_power} W")
            for device in sorted(device_list, key=lambda d: d["priority"]):
                if not device.get("disabled_by_manager", False):
                    device["initial_state"] = hass.states.get(device["entity_id"]).state
                    device["disabled_by_manager"] = True
        else:
            hass.states.async_set(f"{DOMAIN}.status", f"Normal: {total_power} W")
            for device in device_list:
                if device.get("disabled_by_manager", False) and device["initial_state"] == "on":
                    device["disabled_by_manager"] = False

    async_track_state_change_event(hass, energy_sensor, energy_monitor)
    hass.states.async_set(f"{DOMAIN}.status", "Monitoring started")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharger l'entrée."""
    if entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]
    return True
