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

    # Vérifier si le capteur de consommation est défini
    if not energy_sensor:
        hass.states.async_set(f"{DOMAIN}.status", "Error: No energy sensor defined")
        return False

    # Initialiser l'état pour chaque périphérique
    for device in device_list:
        entity_id = device.get("entity_id", "")
        priority = device.get("priority", 1)
        energy_usage = device.get("energy_usage", 0)
        disabled_by_manager = device.get("disabled_by_manager", False)
        initial_state = hass.states.get(entity_id).state if hass.states.get(entity_id) else "unknown"

        # Mettre à jour l'état dans Home Assistant
        hass.states.async_set(
            f"{DOMAIN}.{entity_id.replace('.', '_')}",
            "Monitored",
            {
                "priority": priority,
                "energy_usage": energy_usage,
                "disabled_by_manager": disabled_by_manager,
                "initial_state": initial_state,
            },
        )

    # Fonction pour surveiller le capteur de consommation
    async def energy_monitor(event):
        """Surveiller les changements d'état du capteur de consommation."""
        state = hass.states.get(energy_sensor)
        if state is not None and state.state:  # Vérifier si l'état est défini
            try:
                current_consumption = float(state.state)
                if current_consumption > max_threshold:
                    # Déclencher une alerte si le seuil est dépassé
                    hass.states.async_set(f"{DOMAIN}.status", f"Over threshold: {current_consumption} W")

                    # Gérer les périphériques à désactiver
                    for device in sorted(device_list, key=lambda x: x["priority"]):
                        if not device.get("disabled_by_manager", False):
                            entity_id = device["entity_id"]
                            initial_state = hass.states.get(entity_id).state
                            device["initial_state"] = initial_state
                            device["disabled_by_manager"] = True
                            hass.states.async_set(
                                f"{DOMAIN}.{entity_id.replace('.', '_')}",
                                "Disabled",
                                device,
                            )
                            # Ici, désactivez le périphérique via une automatisation ou une API

                else:
                    # Sinon, tout est normal
                    hass.states.async_set(f"{DOMAIN}.status", f"Normal: {current_consumption} W")

                    # Réactiver les périphériques si nécessaires
                    for device in device_list:
                        if device.get("disabled_by_manager", False) and device["initial_state"] == "on":
                            entity_id = device["entity_id"]
                            device["disabled_by_manager"] = False
                            hass.states.async_set(
                                f"{DOMAIN}.{entity_id.replace('.', '_')}",
                                "Enabled",
                                device,
                            )
                            # Ici, réactivez le périphérique via une automatisation ou une API

            except ValueError:
                # L'état n'est pas un nombre
                hass.states.async_set(f"{DOMAIN}.status", "Error: Sensor state is not numeric")
        else:
            # L'état du capteur est invalide ou non défini
            hass.states.async_set(f"{DOMAIN}.status", "Error: Invalid or missing sensor state")

    # Surveiller les changements d'état du capteur
    async_track_state_change_event(hass, energy_sensor, energy_monitor)

    # Définir un état initial pour le gestionnaire
    hass.states.async_set(f"{DOMAIN}.status", "Monitoring started")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharger l'entrée."""
    if entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]
    return True
