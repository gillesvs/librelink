"""Custom integration to integrate LibreLink with Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LibreLinkAPI
from .const import CONF_PATIENT_ID, DOMAIN, LOGGER
from .coordinator import LibreLinkDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""

    LOGGER.debug(
        "Appel de async_setup_entry entry: entry_id= %s, data= %s",
        entry.entry_id,
        entry.data,
    )

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    base_url = entry.data[CONF_URL]
    patient_id = entry.data[CONF_PATIENT_ID]

    domain_data = hass.data.setdefault(DOMAIN, {})

    if username not in domain_data:
        # Using the declared API for login based on patient credentials to retreive the bearer Token
        api = LibreLinkAPI(
            base_url=base_url,
            session=async_get_clientsession(hass),
        )

        # Then getting the token.
        await api.async_login(username=username, password=password)

        coordinator = LibreLinkDataUpdateCoordinator(
            hass=hass, api=api, patient_id=patient_id
        )

        # First poll of the data to be ready for entities initialization
        await coordinator.async_config_entry_first_refresh()

        domain_data[username] = coordinator
    else:
        coordinator: LibreLinkDataUpdateCoordinator = domain_data[username]
        coordinator.register_patient(patient_id)

    # Then launch async_setup_entry for our declared entities in sensor.py and binary_sensor.py
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: LibreLinkDataUpdateCoordinator = hass.data[DOMAIN][CONF_USERNAME]
        coordinator.unregister_patient(entry.data[CONF_PATIENT_ID])
        if coordinator.tracked_patients == 0:
            hass.data[DOMAIN].pop(CONF_USERNAME)
    return unloaded
