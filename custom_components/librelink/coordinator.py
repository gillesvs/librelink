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
from .const import DOMAIN, LOGGER, REFRESH_RATE_MIN


class LibreLinkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API. single endpoint"""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: LibreLinkApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        self.api: LibreLinkApiClient = client

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=REFRESH_RATE_MIN),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except LibreLinkApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except LibreLinkApiError as exception:
            raise UpdateFailed(exception) from exception
