"""Sensor platform for LibreLink."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import LibreLinkDataUpdateCoordinator

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LibreLinkDataUpdateCoordinator

import logging

# enable logging
_LOGGER = logging.getLogger(__name__)


# This class is called when a device is created.
# A device is created for each patient to regroup patient entities

class LibreLinkDevice(CoordinatorEntity):
    """LibreLinkEntity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        patientId: str,
        patient: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        # Creating unique IDs using for the device based on the Librelink patient Id.
        self._attr_unique_id = f"{patientId}"
        _LOGGER.debug(
            "entity unique id is %s",
            self._attr_unique_id,
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, patientId)},
            name=patient,
            model=VERSION,
            manufacturer=NAME,
        )

