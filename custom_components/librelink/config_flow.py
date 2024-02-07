"""Adds config flow for LibreLink."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_UNIT_OF_MEASUREMENT, CONF_URL, CONF_COUNTRY
from homeassistant.helpers import selector, config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import callback

from .api import (
    LibreLinkApiLogin,
    LibreLinkApiAuthenticationError,
    LibreLinkApiCommunicationError,
    LibreLinkApiError,
)
from .const import DOMAIN, LOGGER, MMOL_L, MG_DL, BASE_URL_LIST, BASE_URL_DEFAULT, BASE_URL

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
                    base_url=user_input[BASE_URL],
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

                    vol.Required(BASE_URL, description = "url by country", default=(BASE_URL_LIST[0])): vol.In(BASE_URL_LIST),


                }),

            errors=_errors,
        )



    async def _test_credentials(self, username: str, password: str, base_url: str) -> None:
        """Validate credentials."""
        client = LibreLinkApiLogin(
            username=username,
            password=password,
            base_url=base_url,
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


    # """Setup sensors from a config entry created in the integrations UI."""
    # config = hass.data[DOMAIN][config_entry.entry_id]
    # session = async_get_clientsession(hass)
    # github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
    # sensors = [GitHubRepoSensor(github, repo) for repo in config[CONF_REPOS]]

        # Grab all configured repos from the entity registry so we can populate the
        # multi-select dropdown that will allow a user to remove a repo.
        # entity_registry = await async_get_registry(self.hass)
        # entries = async_entries_for_config_entry(
        #     entity_registry, self.config_entry.entry_id
        # )
        # Default value for our multi-select.


        # all_repos = {e.entity_id: e.original_name for e in entries}
        # repo_map = {e.entity_id: e for e in entries}

        # if user_input is not None:
        #     # Validation and additional processing logic omitted for brevity.
        #     # ...
        #     if not errors:
        #         # Value of data will be set on the options property of our config_entry
        #         # instance.
        #         return self.async_create_entry(
        #             title="",
        #             data={CONF_REPOS: updated_repos},
        #         )

        # options_schema = vol.Schema(
        #     {
        #         vol.Optional("repos", default=list(all_repos.keys())): cv.multi_select(
        #             all_repos
        #         ),
        #         vol.Optional(CONF_PATH): cv.string,
        #         vol.Optional(CONF_NAME): cv.string,
        #     }
        # )
        # return self.async_show_form(
        #     step_id="init", data_schema=options_schema, errors=errors
        # )