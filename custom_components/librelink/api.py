"""I used the https://libreview-unofficial.stoplight.io/docs/libreview-unofficial/ as a starting point to use the Abbot Libreview API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
import socket

import aiohttp

from .const import (
    API_TIME_OUT_SECONDS,
    CONNECTION_URL,
    LOGGER,
    LOGIN_URL,
    PRODUCT,
    VERSION_APP,
)


@dataclass
class Target:
    """Target Glucose data."""

    high: int
    low: int


@dataclass
class Measurement:
    """Measurement data."""

    value: int
    timestamp: datetime
    trend: int


@dataclass
class LibreLinkDevice:
    """LibreLink device data."""

    serial_number: str
    application_timestamp: datetime | None

    @property
    def expiration_timestamp(self):
        """Return the expiration timestamp of the sensor."""
        return self.application_timestamp + timedelta(days=14)


@dataclass
class Patient:
    """Patient data."""

    id: str
    first_name: str
    last_name: str
    measurement: Measurement
    target: Target
    device: LibreLinkDevice

    @property
    def name(self):
        """Return the full name of the patient."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_api_response_data(cls, data):
        """Create a Patient object from the API response data."""
        return cls(
            id=data["patientId"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            measurement=Measurement(
                value=data["glucoseMeasurement"]["ValueInMgPerDl"],
                timestamp=datetime.strptime(
                    data["glucoseMeasurement"]["FactoryTimestamp"],
                    "%m/%d/%Y %I:%M:%S %p",
                ).replace(tzinfo=UTC),
                trend=data["glucoseMeasurement"]["TrendArrow"],
            ),
            target=Target(
                high=data["targetHigh"],
                low=data["targetLow"],
            ),
            device=LibreLinkDevice(
                serial_number=f'{data["sensor"]["pt"]}{data['sensor']['sn']}',
                application_timestamp=datetime.fromtimestamp(
                    data["sensor"]["a"], tz=UTC
                ),
            ),
        )


class LibreLinkAPIError(Exception):
    """Base class for exceptions in this module."""


class LibreLinkAPIAuthenticationError(LibreLinkAPIError):
    """Exception raised when the API authentication fails."""

    def __init__(self) -> None:
        """Initialize the API error."""
        super().__init__("Invalid credentials")


class LibreLinkAPIConnectionError(LibreLinkAPIError):
    """Exception raised when the API connection fails."""

    def __init__(self, message: str = None) -> None:
        """Initialize the API error."""
        super().__init__(message or "Connection error")


class LibreLinkAPI:
    """API class for communication with the LibreLink API."""

    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._token = None
        self._account_id = None
        self._session = session
        self.base_url = base_url

    async def async_get_data(self):
        """Get data from the API."""
        response = await self._call_api(url=CONNECTION_URL)
        LOGGER.debug("Return API Status:%s ", response["status"])
        # API status return 0 if everything goes well.
        if response["status"] != 0:
            raise LibreLinkAPIConnectionError()

        patients = [
            Patient.from_api_response_data(patient) for patient in response["data"]
        ]

        LOGGER.debug(
            "Number of patients : %s and patient list %s", len(patients), patients
        )
        self._token = response["ticket"]["token"]

        return patients

    async def async_login(self, username: str, password: str) -> str:
        """Get token from the API."""
        response = await self._call_api(
            url=LOGIN_URL,
            data={"email": username, "password": password},
            authenticated=False,
        )
        LOGGER.debug("Login status : %s", response["status"])
        if response["status"] == 2:
            raise LibreLinkAPIAuthenticationError()

        self._token = response["data"]["authTicket"]["token"]
        self._account_id = response["data"]["user"]["id"]

    async def _call_api(
        self,
        url: str,
        data: dict | None = None,
        authenticated: bool = True,
    ) -> any:
        """Get information from the API."""
        headers = {
            "product": PRODUCT,
            "version": VERSION_APP,
        }
        if authenticated:
            headers |= {
                'Authorization': f'Bearer {self._token}',
                'Account-Id': sha256(self._account_id.encode()).hexdigest()
            }

        call_method = self._session.post if data else self._session.get
        try:
            response = await call_method(
                url=self.base_url + url,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=API_TIME_OUT_SECONDS),
            )
            LOGGER.debug("response.status: %s", response.status)
            if response.status in (401, 403):
                raise LibreLinkAPIAuthenticationError()
            response.raise_for_status()
            return await response.json()
        except TimeoutError as e:
            raise LibreLinkAPIConnectionError("Timeout Error") from e
        except (aiohttp.ClientError, socket.gaierror) as e:
            raise LibreLinkAPIConnectionError() from e
        except Exception as e:
            raise LibreLinkAPIError() from e
