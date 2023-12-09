"""Sensor platform for LibreLink."""


from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant

from datetime import datetime
import time

from .entity import LibreLinkEntity

from .const import (
    DOMAIN,
    GLUCOSE_VALUE_ICON,
    GLUCOSE_TREND_ICON,
    GLUCOSE_TREND_MESSAGE,
    MG_DL,
)
from .coordinator import LibreLinkDataUpdateCoordinator


from .coordinator import LibreLinkDataUpdateCoordinator

import logging

# GVS: Tuto pour ajouter des log
_LOGGER = logging.getLogger(__name__)

""" Three sensors are declared:
    Glucose Value
    Glucose Trend
    Sensor days and related sensor attributes"""

SensorDescription = (
    SensorEntityDescription(
        key="value",
        name="Glucose Measurement",
        #        icon = GLUCOSE_VALUE_ICON, #"mdi:cellphone-arrow-down-variant",
        unit_of_measurement=MG_DL,
    ),
    SensorEntityDescription(
        key="trend",
        name="Glucose Trend",
    ),
    SensorEntityDescription(
        key="sensor",
        name="Active Sensor",
        unit_of_measurement="days",
    ),
    SensorEntityDescription(
        key="delay",
        name="Minutes since update",
        unit_of_measurement="min",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    usermail = (config_entry.data[CONF_USERNAME]).split("@")
    username = usermail[0]

    # I add my three sensors all instantiating a new class LibreLinSensor
    async_add_entities(
        LibreLinkSensor(
            coordinator, username, config_entry.entry_id, entity_description
        )
        for entity_description in SensorDescription
    )


class LibreLinkSensor(LibreLinkEntity, SensorEntity):
    """LibreLink Sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        username: str,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, username, entry_id, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        """Return the native value of the sensor."""

        result = None

        if self.coordinator.data:
            if self.entity_description.key == "value":
                result = int(
                    (
                        self.coordinator.data["data"][0]["glucoseMeasurement"][
                            "ValueInMgPerDl"
                        ]
                    )
                )

            elif self.entity_description.key == "trend":
                result = GLUCOSE_TREND_MESSAGE[
                    (
                        self.coordinator.data["data"][0]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]

            elif self.entity_description.key == "sensor":
                result = int(
                    (time.time() - (self.coordinator.data["data"][0]["sensor"]["a"]))
                    / 86400
                )

            elif self.entity_description.key == "delay":
                result = int(
                    (
                        datetime.now()
                        - datetime.strptime(
                            self.coordinator.data["data"][0]["glucoseMeasurement"][
                                "Timestamp"
                            ],
                            "%m/%d/%Y %I:%M:%S %p",
                        )
                    ).total_seconds()
                    / 60
                )

            return result
        return None

    @property
    def icon(self):
        """Return the icon for the frontend."""

        if self.coordinator.data:
            if self.entity_description.key in ["value", "trend"]:
                return GLUCOSE_TREND_ICON[
                    (
                        self.coordinator.data["data"][0]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]
        return GLUCOSE_VALUE_ICON

    @property
    def unit_of_measurement(self):
        """Return the icon for the frontend."""

        if self.coordinator.data:
            if self.entity_description.key in ["value", "sensor"]:
                return self.entity_description.unit_of_measurement
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        result = None
        if self.coordinator.data:
            if self.entity_description.key == "sensor":
                result = {
                    "Serial number": f"{self.coordinator.data['data'][0]['sensor']['pt']} {self.coordinator.data['data'][0]['sensor']['sn']}",
                    "Activation date": datetime.fromtimestamp(
                        (self.coordinator.data["data"][0]["sensor"]["a"])
                    ),
                    "patientId": self.coordinator.data["data"][0]["patientId"],
                    "Patient": f"{(self.coordinator.data['data'][0]['lastName']).upper()} {self.coordinator.data['data'][0]['firstName']}",
                }

            return result
        return result
