"""Sensor platform for LibreLink."""


from __future__ import annotations
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_UNIT_OF_MEASUREMENT
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


SensorDescription = (
    SensorEntityDescription(
        key="value",
        name="Glucose Measurement",
        #        icon = GLUCOSE_VALUE_ICON, #"mdi:cellphone-arrow-down-variant",
        # unit_of_measurement=MG_DL,
        # unit_of_measurement = config_entry.options[CONF_UNIT_OF_MEASUREMENT],
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
    # usermail = (config_entry.data[CONF_USERNAME]).split("@")
    # username = usermail[0]
    #    print(f"Unit: {config_entry.options[CONF_UNIT_OF_MEASUREMENT]}")
    try:
        custom_unit = config_entry.options[CONF_UNIT_OF_MEASUREMENT]
    except KeyError:
        custom_unit = MG_DL

    # Starts here, for each patients, new entity base on patients and not user
    # using an index as we need to keep the coordinator in the @property to get updates from coordinator

    for index, patients in enumerate(coordinator.data["data"]):
#        print(index, patients)

    # for patients in coordinator.data["data"]:
        patient = patients["firstName"] + " " + patients["lastName"]
        patientId = patients["patientId"]
#        print(f"patient : {patient}")


        # I add my three sensors all instantiating a new class LibreLinSensor
        async_add_entities(
            LibreLinkSensor(
                coordinator,
                patients,
                patientId,
                patient,
                index,
                config_entry.entry_id,
                custom_unit,
                entity_description,
            )
            for entity_description in SensorDescription

        )


class LibreLinkSensor(LibreLinkEntity, SensorEntity):
    """LibreLink Sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        patients,
        patientId: str,
        patient: str,
        index: int,
        entry_id: str,
        uom: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, patientId, patient, entry_id, description.key)
        self.entity_description = description
        self.uom = uom
        self.index = index
        self.patients = patients

    @property
    def native_value(self):
        """Return the native value of the sensor."""

        result = None

        if self.patients:
            if self.entity_description.key == "value":
                if self.uom == MG_DL:
                    result = int(
                        (
                            self.coordinator.data["data"][self.index]["glucoseMeasurement"][
                                "ValueInMgPerDl"
                            ]
                        )
                    )
                if self.uom == MMOL_L:
                    result = round(
                        float(
                            (
                                self.coordinator.data["data"][self.index]["glucoseMeasurement"][
                                    "ValueInMgPerDl"
                                ]
                                / MMOL_DL_TO_MG_DL
                            )
                        ),
                        1,
                    )

            elif self.entity_description.key == "trend":
                result = GLUCOSE_TREND_MESSAGE[
                    (
                        self.coordinator.data["data"][self.index]["glucoseMeasurement"][
                            "TrendArrow"
                        ]
                    )
                    - 1
                ]

            elif self.entity_description.key == "sensor":
                result = int(
                    (time.time() - (self.coordinator.data["data"][self.index]["sensor"]["a"]))
                    / 86400
                )

            elif self.entity_description.key == "delay":
                result = int(
                    (
                        datetime.now()
                        - datetime.strptime(
                            self.coordinator.data["data"][self.index]["glucoseMeasurement"][
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

        if self.coordinator.data["data"][self.index]:
            if self.entity_description.key in ["value", "trend"]:
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
        """Return the icon for the frontend."""

        if self.coordinator.data["data"][self.index]:
            if self.entity_description.key in ["sensor"]:
                return self.entity_description.unit_of_measurement
            elif self.entity_description.key in ["value"]:
                return self.uom
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        result = None
        if self.coordinator.data["data"][self.index]:
            if self.entity_description.key == "sensor":
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
