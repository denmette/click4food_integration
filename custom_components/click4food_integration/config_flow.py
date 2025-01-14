"""Adds config flow for Click 4 Food."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import (
    callback,
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    Click4FoodApiClient,
    Click4FoodApiClientAuthenticationError,
    Click4FoodApiClientCommunicationError,
    Click4FoodApiClientError,
)
from .const import DOMAIN, LOGGER


def _get_data_schema(config_entry: ConfigEntry | None = None) -> vol.Schema:
    """Get a schema with default values."""
    default_username = config_entry.data.get(CONF_USERNAME) if config_entry else None
    default_password = config_entry.data.get(CONF_PASSWORD) if config_entry else None

    return vol.Schema(
        {
            vol.Required(
                CONF_USERNAME, default=default_username
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
            vol.Required(
                CONF_PASSWORD, default=default_password
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
        }
    )


class Click4FoodFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Click4Food."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except Click4FoodApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except Click4FoodApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except Click4FoodApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(unique_id=DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Click4Food - Compass Group",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_get_data_schema(),
            errors=_errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> Click4FoodOptionsFlowHandler:
        """Create the options flow."""
        return Click4FoodOptionsFlowHandler(config_entry)

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        client = Click4FoodApiClient(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.login()


class Click4FoodOptionsFlowHandler(OptionsFlow):
    """Options flow for Click4Food component."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry with data from user input
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(
                title=self.config_entry.title, data=user_input
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_get_data_schema(config_entry=self.config_entry),
        )
