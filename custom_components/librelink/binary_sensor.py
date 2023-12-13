"""Binary sensor platform for librelink."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant


from .const import DOMAIN
from .coordinator import LibreLinkDataUpdateCoordinator
from .entity import LibreLinkEntity

import logging

# GVS: Tuto pour ajoute r des log
_LOGGER = logging.getLogger(__name__)


BinarySensorDescription = (
    BinarySensorEntityDescription(
        key="isHigh",
        name="Is High",
    ),
    BinarySensorEntityDescription(
        key="isLow",
        name="Is Low",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    usermail = (config_entry.data[CONF_USERNAME]).split("@")
    username = usermail[0]
    async_add_entities(
        LibreLinkBinarySensor(
            coordinator,
            username,
            config_entry.entry_id,
            entity_description,
        )
        for entity_description in BinarySensorDescription
    )


class LibreLinkBinarySensor(LibreLinkEntity, BinarySensorEntity):
    """librelink binary_sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        username: str,
        entry_id,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, username, entry_id, description.key)
        self.entity_description = description

    # define state based on the entity_description key
    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.data["data"][0]["glucoseMeasurement"][
            self.entity_description.key
        ]

