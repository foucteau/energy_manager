"""Constants for the Energy Manager integration."""
DOMAIN = "energy_manager"

# Modèle par défaut pour un périphérique
DEVICE_SCHEMA = {
    "entity_id": "",
    "priority": 1,
    "energy_usage": 0,  # Mesurée en watts lors de la coupure
    "disabled_by_manager": False,
    "initial_state": "unknown",  # État initial avant coupure (on/off)
}
