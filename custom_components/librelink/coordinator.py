"""DataUpdateCoordinator for LibreLink."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import LibreLinkAPI, Patient
from .const import DOMAIN, LOGGER, REFRESH_RATE_MIN


class LibreLinkDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Patient]]):
    """Class to manage fetching data from the API. single endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: LibreLinkAPI,
        patient_id: str,
    ) -> None:
        """Initialize."""
        self.api: LibreLinkAPI = api
        self._tracked_patients: set[str] = {patient_id}

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=REFRESH_RATE_MIN),
        )

    def register_patient(self, patient_id: str) -> None:
        """Register a new patient to track."""
        self._tracked_patients.add(patient_id)

    def unregister_patient(self, patient_id: str) -> None:
        """Unregister a patient to track."""
        self._tracked_patients.remove(patient_id)

    @property
    def tracked_patients(self) -> int:
        """Return the number of tracked patients."""
        return len(self._tracked_patients)

    async def _async_update_data(self):
        """Update data via library."""
        return {patient.id: patient for patient in await self.api.async_get_data()}
