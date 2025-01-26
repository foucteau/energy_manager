"""Config flow for Energy Manager."""
from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN

class EnergyManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Energy Manager", data=user_input)

        # Formulaire de configuration initiale
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("max_energy_threshold", default=3000): int,  # Seuil max (en watts)
                vol.Required("energy_sensor", description="Capteur de consommation totale"):
                    selector.EntitySelector({ "domain": "sensor" }),  # Capteur
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Retourne le flux des options."""
        return EnergyManagerOptionsFlow(config_entry)

class EnergyManagerOptionsFlow(config_entries.OptionsFlow):
    """Gestion des options pour Energy Manager."""

    def __init__(self, config_entry):
        """Initialiser les options."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Gérer les options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Formulaire pour mettre à jour la configuration
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("max_energy_threshold", default=self.config_entry.options.get("max_energy_threshold", 3000)): int,
                vol.Required("energy_sensor", default=self.config_entry.options.get("energy_sensor", "")):
                    selector.EntitySelector({ "domain": "sensor" }),
            }),
        )
