"""Sensor platform for LibreLink."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_PATIENT_ID,
    DOMAIN,
    GLUCOSE_TREND_ICON,
    GLUCOSE_TREND_MESSAGE,
    GLUCOSE_VALUE_ICON,
    NAME,
    VERSION,
)
from .coordinator import LibreLinkDataUpdateCoordinator
from .units import UNITS_OF_MEASUREMENT, UnitOfMeasurement


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.data[CONF_USERNAME]]

    # If custom unit of measurement is selectid it is initialized, otherwise MG/DL is used
    unit = {u.unit_of_measurement: u for u in UNITS_OF_MEASUREMENT}.get(
        config_entry.data[CONF_UNIT_OF_MEASUREMENT]
    )
    pid = config_entry.data[CONF_PATIENT_ID]

    # For each patients, new Device base on patients and
    # using an index as we need to keep the coordinator in the @property to get updates from coordinator
    # we create an array of entities then create entities.

    sensors = [
        MeasurementSensor(coordinator, pid, unit),
        TrendSensor(coordinator, pid),
        ApplicationTimestampSensor(coordinator, pid),
        ExpirationTimestampSensor(coordinator, pid),
        LastMeasurementTimestampSensor(coordinator, pid),
    ]

    async_add_entities(sensors)


class LibreLinkSensorBase(CoordinatorEntity[LibreLinkDataUpdateCoordinator]):
    """LibreLink Sensor base class."""

    def __init__(self, coordinator: LibreLinkDataUpdateCoordinator, pid: str) -> None:
        """Initialize the device class."""
        super().__init__(coordinator)

        self.id = pid

    @property
    def device_info(self):
        """Return the device info of the sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._data.id)},
            name=self._data.name,
            model=VERSION,
            manufacturer=NAME,
        )

    @property
    def attribution(self):
        """Return the attribution for this entity."""
        return ATTRIBUTION

    @property
    def has_entity_name(self):
        """Return if the entity has a name."""
        return True

    @property
    def _data(self):
        return self.coordinator.data[self.id]

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return f"{self._data.id} {self.name}".replace(" ", "_").lower()


class LibreLinkSensor(LibreLinkSensorBase, SensorEntity):
    """LibreLink Sensor class."""

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return GLUCOSE_VALUE_ICON


class TrendSensor(LibreLinkSensor):
    """Glucose Trend Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Trend"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return GLUCOSE_TREND_MESSAGE[self._data.measurement.trend]

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return GLUCOSE_TREND_ICON[self._data.measurement.trend]


class MeasurementSensor(TrendSensor, LibreLinkSensor):
    """Glucose Measurement Sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        pid: str,
        unit: UnitOfMeasurement,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, pid)
        self.unit = unit

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Measurement"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.unit.from_mg_per_dl(self._data.measurement.value)

    @property
    def suggested_display_precision(self):
        """Return the suggested precision of the sensor."""
        return self.unit.suggested_display_precision

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return self.unit.unit_of_measurement


class TimestampSensor(LibreLinkSensor):
    """Timestamp Sensor class."""

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SensorDeviceClass.TIMESTAMP


class ApplicationTimestampSensor(TimestampSensor):
    """Sensor Days Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Application Timestamp"

    @property
    def available(self):
        """Return if the sensor data are available."""
        return self._data.device.application_timestamp is not None

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._data.device.application_timestamp

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the librelink sensor."""
        attrs = {
            "Patient ID": self._data.id,
            "Patient": self._data.name,
        }
        if self.available:
            attrs |= {
                "Serial number": self._data.device.serial_number,
                "Activation date": self._data.device.application_timestamp,
            }

        return attrs


class ExpirationTimestampSensor(ApplicationTimestampSensor):
    """Sensor Days Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Expiration Timestamp"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._data.device.expiration_timestamp


class LastMeasurementTimestampSensor(TimestampSensor):
    """Sensor Delay Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Last Measurement Timestamp"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._data.measurement.timestamp
