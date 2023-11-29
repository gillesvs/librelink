"""Sensor platform for LibreLink."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import LibreLinkDataUpdateCoordinator

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LibreLinkDataUpdateCoordinator

import logging

# GVS: Tuto pour ajouter des log
_LOGGER = logging.getLogger(__name__)



class LibreLinkEntity(CoordinatorEntity):
    """LibreLinkEntity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: LibreLinkDataUpdateCoordinator, username: str, entry_id: str, key: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        # Creating unique IDs using sensor key.
        self._attr_unique_id = f"{username}-{entry_id}-{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name= username,
            model=VERSION,
            manufacturer=NAME,
        )