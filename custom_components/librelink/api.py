"""I used the https://libreview-unofficial.stoplight.io/docs/libreview-unofficial/ as a starting point to use the Abbot Libreview API."""

from __future__ import annotations

import asyncio
import logging
import socket
import hashlib

import aiohttp

from .const import (
    API_TIME_OUT_SECONDS,
    APPLICATION,
    CONNECTION_URL,
    LOGIN_URL,
    PRODUCT,
    VERSION_APP,
)

_LOGGER = logging.getLogger(__name__)


class LibreLinkApiClient:
    """API class to retriev measurement data.

    Attributes:
        token: The long life token to authenticate.
        base_url: For API calls depending on your location
        Session: aiottp object for the open session
    """

    def __init__(
        self, token: str, accountId: str, base_url: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._token = token
        # Since only the hashed account id is required in later request, already hash it here 
        self._hashedAccountId = hashlib.sha256(accountId.encode('utf-8')).hexdigest()
        self._session = session
        self.connection_url = base_url + CONNECTION_URL

    async def async_get_data(self) -> any:
        """Get data from the API."""
        APIreponse = await api_wrapper(
            self._session,
            method="get",
            url=self.connection_url,
            headers={
                "product": PRODUCT,
                "version": VERSION_APP,
                "Application": APPLICATION,
                "Authorization": "Bearer " + self._token,
                "Account-Id": self._hashedAccountId
            },
            data={},
        )

        # Ordering API response by patients as the API does not always send patients in the same order
        # This temporary solution works only when you do not add a new Patient in your account.
        # HELP NEEDED - If your fork this project, find a way to navigate through the API response without mixing patients when they arrive in a different order. Strangely, Index numbers are not reevaluated by existing sensors when updated.
        # Sorting patients is ok until you add a new patients and then it mixed up indexes. So the solution is to delete the integration and reinstall it when you want to add a patient.

        _LOGGER.debug(
            "Return API Status:%s ",
            APIreponse["status"],
        )

        # API status return 0 if everything goes well.
        if APIreponse["status"] == 0:
            patients = sorted(APIreponse["data"], key=lambda x: x["patientId"])
        else:
            patients = APIreponse  # to be used for debugging in status not ok

        _LOGGER.debug(
            "Number of patients : %s and patient list %s",
            len(patients),
            patients,
        )

        return patients


class LibreLinkGetGraph:
    """API class to retriev measurement data.

    Attributes:
        token: The long life token to authenticate.
        base_url: For API calls depending on your location
        Session: aiottp object for the open session
        patientId: As this API retreive data for a specified patient
    """

    def __init__(
        self, token: str, base_url: str, session: aiohttp.ClientSession, patient_id: str
    ) -> None:
        """Sample API Client."""
        self._token = token
        self._session = session
        self.connection_url = base_url + CONNECTION_URL
        self.patient_id = patient_id

    async def async_get_data(self) -> any:
        """Get data from the API."""
        APIreponse = await api_wrapper(
            self._session,
            method="get",
            url=self.connection_url,
            headers={
                "product": PRODUCT,
                "version": VERSION_APP,
                "Application": APPLICATION,
                "Authorization": "Bearer " + self._token,
                "patientid": self.patient_id,
            },
            data={},
        )

        _LOGGER.debug(
            "Get Connection : %s",
            APIreponse,
        )

        return APIreponse


class LibreLinkApiLogin:
    """API class to retriev token.

    Attributes:
        username: of the librelink account
        password: of the librelink account
        base_url: For API calls depending on your location
        Session: aiottp object for the open session
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self.login_url = base_url + LOGIN_URL
        self._session = session

    async def async_get_token(self) -> any:
        """Get token from the API."""
        reponseLogin = await api_wrapper(
            self._session,
            method="post",
            url=self.login_url,
            headers={
                "product": PRODUCT,
                "version": VERSION_APP,
                "Application": APPLICATION,
            },
            data={"email": self._username, "password": self._password},
        )
        _LOGGER.debug(
            "Login status : %s",
            reponseLogin["status"],
        )
        if reponseLogin["status"]==2:
            raise LibreLinkApiAuthenticationError(
                "Invalid credentials",
            )

        monToken = reponseLogin["data"]["authTicket"]["token"]
        accountId = reponseLogin["data"]["user"]["id"]

        return monToken, accountId


################################################################
#            """Utilitises """               #
################################################################


@staticmethod
async def api_wrapper(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    data: dict | None = None,
    headers: dict | None = None,
) -> any:
    """Get information from the API."""
    try:
        async with asyncio.timeout(API_TIME_OUT_SECONDS):
            response = await session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
            )
            _LOGGER.debug("response.status: %s", response.status)
            if response.status in (401, 403):
                raise LibreLinkApiAuthenticationError(
                    "Invalid credentials",
                )
            response.raise_for_status()
            #
            return await response.json()

    except asyncio.TimeoutError as exception:
        raise LibreLinkApiCommunicationError(
            "Timeout error fetching information",
        ) from exception
    except (aiohttp.ClientError, socket.gaierror) as exception:
        raise LibreLinkApiCommunicationError(
            "Error fetching information",
        ) from exception
    except Exception as exception:  # pylint: disable=broad-except
        raise LibreLinkApiError("Something really wrong happened!") from exception


class LibreLinkApiError(Exception):
    """Exception to indicate a general API error."""

    _LOGGER.debug("Exception: general API error")


class LibreLinkApiCommunicationError(LibreLinkApiError):
    """Exception to indicate a communication error."""

    _LOGGER.debug("Exception: communication error")


class LibreLinkApiAuthenticationError(LibreLinkApiError):
    """Exception to indicate an authentication error."""

    _LOGGER.debug("Exception: authentication error")
