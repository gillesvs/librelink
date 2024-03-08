"""Sensor platform for LibreLink."""

from __future__ import annotations

from datetime import datetime
import logging
import time

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    GLUCOSE_TREND_ICON,
    GLUCOSE_TREND_MESSAGE,
    GLUCOSE_VALUE_ICON,
    MG_DL,
    MMOL_DL_TO_MG_DL,
    MMOL_L,
)
from .coordinator import LibreLinkDataUpdateCoordinator
from .device import LibreLinkDevice

# GVS: Tuto pour ajouter des log
_LOGGER = logging.getLogger(__name__)

""" Three sensors are declared:
    Glucose Value
    Glucose Trend
    Sensor days and related sensor attributes"""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # If custom unit of measurement is selectid it is initialized, otherwise MG/DL is used
    try:
        custom_unit = config_entry.data[CONF_UNIT_OF_MEASUREMENT]
    except KeyError:
        custom_unit = MG_DL

    # For each patients, new Device base on patients and
    # using an index as we need to keep the coordinator in the @property to get updates from coordinator
    # we create an array of entities then create entities.

    sensors = []
    for index, patients in enumerate(coordinator.data):

        sensors.extend(
            [
                LibreLinkSensor(
                    coordinator,
                    index,
                    "value",  # key
                    "Glucose Measurement",  # name
                    custom_unit,
                ),
                LibreLinkSensor(
                    coordinator,
                    index,
                    "trend",  # key
                    "Trend",  # name
                    custom_unit,
                ),
                LibreLinkSensor(
                    coordinator,
                    index,
                    "sensor",  # key
                    "Active Sensor",  # name
                    "days",  # uom
                ),
                LibreLinkSensor(
                    coordinator,
                    index,
                    "delay",  # key
                    "Minutes since update",  # name
                    "min",  # uom
                ),
            ]
        )

    async_add_entities(sensors)


class LibreLinkSensor(LibreLinkDevice, SensorEntity):
    """LibreLink Sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        index,
        key: str,
        name: str,
        uom,
    ) -> None:
        """Initialize the device class."""
        super().__init__(coordinator, index)
        self.uom = uom
        self.patients = (
            self.coordinator.data[index]["firstName"]
            + " "
            + self.coordinator.data[index]["lastName"]
        )
        self.patientId = self.coordinator.data[index]["patientId"]
        self._attr_unique_id = f"{self.coordinator.data[index]['patientId']}_{key}"
        self._attr_name = name
        self.index = index
        self.key = key

    @property
    def native_value(self):
        """Return the native value of the sensor."""

        result = None

        # to avoid failing requests if there is no activated sensor for a patient.
        if self.coordinator.data[self.index] is not None:
            if self.key == "value":
                if self.uom == MG_DL:
                    result = int(
                        self.coordinator.data[self.index]["glucoseMeasurement"][
                            "ValueInMgPerDl"
                        ]
                    )
                if self.uom == MMOL_L:
                    result = round(
                        float(
                            self.coordinator.data[self.index][
                                "glucoseMeasurement"
                            ]["ValueInMgPerDl"]
                            / MMOL_DL_TO_MG_DL
                        ),
                        1,
                    )

            elif self.key == "trend":
                result = GLUCOSE_TREND_MESSAGE[
                    (
                        self.coordinator.data[self.index]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]

            elif self.key == "sensor":
                if self.coordinator.data[self.index]["sensor"] is not None:
                    result = int(
                        (
                            time.time()
                            - (self.coordinator.data[self.index]["sensor"]["a"])
                        )
                        / 86400
                    )

            elif self.key == "delay":
                result = int(
                    (
                        datetime.now()
                        - datetime.strptime(
                            self.coordinator.data[self.index][
                                "glucoseMeasurement"
                            ]["Timestamp"],
                            "%m/%d/%Y %I:%M:%S %p",
                        )
                    ).total_seconds()
                    / 60  # convert seconds in minutes
                )

            return result
        return None

    @property
    def icon(self):
        """Return the icon for the frontend."""

        if self.coordinator.data[self.index]["glucoseMeasurement"]["TrendArrow"]:
            if self.key in ["value", "trend"]:
                return GLUCOSE_TREND_ICON[
                    (
                        self.coordinator.data[self.index]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]
        return GLUCOSE_VALUE_ICON

    @property
    def unit_of_measurement(self):
        """Only used for glucose measurement and librelink sensor delay since update."""

        if self.coordinator.data[self.index]:
            if self.key in ["sensor", "value"]:
                return self.uom
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the librelink sensor."""
        result = None
        if self.coordinator.data[self.index]:
            if self.key == "sensor":
                if self.coordinator.data[self.index]["sensor"] is not None:
                    result = {
                        "Serial number": f"{self.coordinator.data[self.index]['sensor']['pt']} {self.coordinator.data[self.index]['sensor']['sn']}",
                        "Activation date": datetime.fromtimestamp(
                            self.coordinator.data[self.index]["sensor"]["a"]
                        ),
                        "patientId": self.coordinator.data[self.index]["patientId"],
                        "Patient": f"{(self.coordinator.data[self.index]['lastName']).upper()} {self.coordinator.data[self.index]['firstName']}",
                    }

            return result
        return result
