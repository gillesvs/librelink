"""Sensor platform for LibreLink."""


from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant
from datetime import datetime
import time
from .device import LibreLinkDevice
from .const import (
    DOMAIN,
    GLUCOSE_VALUE_ICON,
    GLUCOSE_TREND_ICON,
    GLUCOSE_TREND_MESSAGE,
    MG_DL,
    MMOL_L,
    MMOL_DL_TO_MG_DL,
)
from .coordinator import LibreLinkDataUpdateCoordinator

import logging

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
        custom_unit = config_entry.options[CONF_UNIT_OF_MEASUREMENT]
    except KeyError:
        custom_unit = MG_DL

    # For each patients, new Device base on patients and
    # using an index as we need to keep the coordinator in the @property to get updates from coordinator
    # we create an array of entities then create entities.

    sensors = []
    for index, patients in enumerate(coordinator.data["data"]):
        patient = patients["firstName"] + " " + patients["lastName"]
        patientId = patients["patientId"]
        #        print(f"patient : {patient}")
        sensors.extend(
            [
                LibreLinkSensor(
                    coordinator,
                    patients,
                    patientId,
                    patient,
                    index,
                    config_entry.entry_id,
                    "value",  # key
                    "Glucose Measurement",  # name
                    custom_unit,
                ),
                LibreLinkSensor(
                    coordinator,
                    patients,
                    patientId,
                    patient,
                    index,
                    config_entry.entry_id,
                    "trend",  # key
                    "Trend",  # name
                    custom_unit,
                ),
                LibreLinkSensor(
                    coordinator,
                    patients,
                    patientId,
                    patient,
                    index,
                    config_entry.entry_id,
                    "sensor",  # key
                    "Active Sensor",  # name
                    "days",  # uom
                ),
                LibreLinkSensor(
                    coordinator,
                    patients,
                    patientId,
                    patient,
                    index,
                    config_entry.entry_id,
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
        patients,
        patientId: str,
        patient: str,
        index,
        entry_id: str,
        key: str,
        name: str,
        uom,
    ) -> None:
        """Initialize the device class."""
        super().__init__(coordinator, patientId, patient)
        self.uom = uom
        print(f"index : {index}")
        self.patients = patients
        self.patientId = patientId
        print(f"PatientId : {self.patientId}")
        self._attr_unique_id = f"{patientId}_{key}_{index}"
        self._attr_name = name
        self.index = index
        self.key = key

    @property
    def native_value(self):
        """Return the native value of the sensor."""

        result = None

        if self.patients:
            if self.key == "value":
                if self.uom == MG_DL:
                    result = int(
                        (
                            self.coordinator.data["data"][self.index][
                                "glucoseMeasurement"
                            ]["ValueInMgPerDl"]
                        )
                    )
                if self.uom == MMOL_L:
                    result = round(
                        float(
                            (
                                self.coordinator.data["data"][self.index][
                                    "glucoseMeasurement"
                                ]["ValueInMgPerDl"]
                                / MMOL_DL_TO_MG_DL
                            )
                        ),
                        1,
                    )

            elif self.key == "trend":
                result = GLUCOSE_TREND_MESSAGE[
                    (
                        self.coordinator.data["data"][self.index]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]

            elif self.key == "sensor":
                result = int(
                    (
                        time.time()
                        - (self.coordinator.data["data"][self.index]["sensor"]["a"])
                    )
                    / 86400
                )

            elif self.key == "delay":
                result = int(
                    (
                        datetime.now()
                        - datetime.strptime(
                            self.coordinator.data["data"][self.index][
                                "glucoseMeasurement"
                            ]["Timestamp"],
                            "%m/%d/%Y %I:%M:%S %p",
                        )
                    ).total_seconds()
                    / 60 # convert seconds in minutes
                )

            return result
        return None

    @property
    def icon(self):
        """Return the icon for the frontend."""

        if self.coordinator.data["data"][self.index]:
            if self.key in ["value", "trend"]:
                return GLUCOSE_TREND_ICON[
                    (
                        self.coordinator.data["data"][self.index]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]
        return GLUCOSE_VALUE_ICON

    @property
    def unit_of_measurement(self):
        """Only used for glucose measurement and librelink sensor delay since update."""

        if self.coordinator.data["data"][self.index]:
            if self.key in ["sensor", "value"]:
                return self.uom
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the librelink sensor."""
        result = None
        if self.coordinator.data["data"][self.index]:
            if self.key == "sensor":
                result = {
                    "Serial number": f"{self.coordinator.data['data'][self.index]['sensor']['pt']} {self.coordinator.data['data'][self.index]['sensor']['sn']}",
                    "Activation date": datetime.fromtimestamp(
                        (self.coordinator.data["data"][self.index]["sensor"]["a"])
                    ),
                    "patientId": self.coordinator.data["data"][self.index]["patientId"],
                    "Patient": f"{(self.coordinator.data['data'][self.index]['lastName']).upper()} {self.coordinator.data['data'][self.index]['firstName']}",
                }

            return result
        return result
