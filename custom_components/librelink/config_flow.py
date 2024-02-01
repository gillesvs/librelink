"""Adds config flow for LibreLink."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_UNIT_OF_MEASUREMENT
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import callback

from .api import (
    LibreLinkApiLogin,
    LibreLinkApiAuthenticationError,
    LibreLinkApiCommunicationError,
    LibreLinkApiError,
)
from .const import DOMAIN, LOGGER, MMOL_L, MG_DL

import logging

# GVS: Init logger
_LOGGER = logging.getLogger(__name__)


class LibreLinkFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for LibreLink."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except LibreLinkApiAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except LibreLinkApiCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except LibreLinkApiError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        client = LibreLinkApiLogin(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )

        await client.async_get_token()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LibreLinkOptionsFlowHandler:
        """Get the options flow for this handler."""
        return LibreLinkOptionsFlowHandler(config_entry)

    # test credential using the login API which enables to retrieve a token
    # Token is retreived in the __init__.py has it needs to be load at each reboot.


class LibreLinkOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for Dexcom."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UNIT_OF_MEASUREMENT,
                    default=self.config_entry.options.get(
                        CONF_UNIT_OF_MEASUREMENT, MG_DL
                    ),
                ): vol.In({MG_DL, MMOL_L}),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
