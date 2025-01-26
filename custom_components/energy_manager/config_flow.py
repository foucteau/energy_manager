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
                vol.Required("max_energy_threshold", default=3000): int,
                vol.Required("energy_sensor"): selector.EntitySelector({"domain": "sensor"}),
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return EnergyManagerOptionsFlow(config_entry)

class EnergyManagerOptionsFlow(config_entries.OptionsFlow):
    """Gestion des options pour Energy Manager."""

    def __init__(self, config_entry):
        """Initialiser les options."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Afficher la liste des périphériques configurés."""
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_add_device()
            elif user_input["action"] == "modify":
                return await self.async_step_modify_device()
            elif user_input["action"] == "delete":
                return await self.async_step_delete_device()

        device_list = self.config_entry.options.get("device_list", [])
        device_list_str = "\n".join(
            [f"- {device['entity_id']} (Priority: {device['priority']})" for device in device_list]
        ) or "Aucun périphérique configuré."

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action"): vol.In(["add", "modify", "delete"]),
            }),
            description_placeholders={
                "device_list": device_list_str,
            },
        )

    async def async_step_add_device(self, user_input=None):
        """Ajouter un périphérique à la liste."""
        if user_input is not None:
            device_list = self.config_entry.options.get("device_list", [])
            user_input["power_sensor"] = user_input.get("power_sensor", f"sensor.{user_input['entity_id'].split('.')[-1]}_power")
            device_list.append(user_input)
            self.hass.config_entries.async_update_entry(
                self.config_entry, options={"device_list": device_list}
            )
            return self.async_create_entry(title="", data={"device_list": device_list})

        return self.async_show_form(
            step_id="add_device",
            data_schema=vol.Schema({
                vol.Required("entity_id"): selector.EntitySelector({"domain": "switch"}),
                vol.Required("priority", default=1): int,
                vol.Optional("power_sensor"): selector.EntitySelector({"domain": "sensor"}),
            }),
        )
