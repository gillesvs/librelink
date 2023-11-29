"""DataUpdateCoordinator for LibreLink."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    LibreLinkApiClient,
    LibreLinkApiAuthenticationError,
    LibreLinkApiError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class LibreLinkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API. single endpoint """

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: LibreLinkApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        self.api: LibreLinkApiClient = client

        # GVS, super permet d'initialiser à partir des infos de la class mère DataUpdateCoordinator
        # The super() function in Python is used to access the methods and
        # attributes of a parent or sibling class from a subclass.
        # The super() function returns an object that represents the parent class,
        # and allows you to call the parent class's methods without explicitly naming them

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )


    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except LibreLinkApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except LibreLinkApiError as exception:
            raise UpdateFailed(exception) from exception

