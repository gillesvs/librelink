"""I used the https://libreview-unofficial.stoplight.io/docs/libreview-unofficial/ as a starting point to use the Abbot Libreview API."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import socket

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
    """API class to retrieve measurement data with automatic re-authentication."""

    def __init__(
        self,
        token: str,
        base_url: str,
        session: aiohttp.ClientSession,
        account_id: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Sample API Client."""
        self._token = token
        self._session = session
        self._base_url = base_url
        self.connection_url = base_url + CONNECTION_URL
        self._username = username
        self._password = password
        self._reauth_lock = asyncio.Lock()
        self._account_id_hash = self._hash_account_id(account_id)

    @staticmethod
    def _hash_account_id(account_id: str | None) -> str | None:
        """Hash the account ID for the account-id header."""
        if not account_id:
            return None
        return hashlib.sha256(account_id.encode()).hexdigest()

    def _build_headers(self) -> dict:
        """Build headers for data requests."""
        headers = {
            "accept-encoding": "gzip",
            "cache-control": "no-cache",
            "connection": "Keep-Alive",
            "content-type": "application/json",
            "product": PRODUCT,
            "version": VERSION_APP,
            "authorization": "Bearer " + self._token,
        }

        if self._account_id_hash:
            headers["account-id"] = self._account_id_hash

        return headers

    async def _async_refresh_auth(self) -> None:
        """Re-login and replace the stored token/account information."""
        if not self._username or not self._password:
            raise LibreLinkApiAuthenticationError(
                "Cannot refresh authentication without stored credentials",
            )

        async with self._reauth_lock:
            _LOGGER.debug("Refreshing LibreLink authentication token")
            login_client = LibreLinkApiLogin(
                username=self._username,
                password=self._password,
                base_url=self._base_url,
                session=self._session,
            )
            login_response = await login_client.async_get_token()
            self._token = login_response["token"]
            self._account_id_hash = self._hash_account_id(login_response["accountId"])
            _LOGGER.debug("LibreLink authentication token refreshed successfully")

    async def async_get_data(self) -> any:
        """Get data from the API and retry once after auth refresh if needed."""
        try:
            api_response = await api_wrapper(
                self._session,
                method="get",
                url=self.connection_url,
                headers=self._build_headers(),
                data={},
            )
        except LibreLinkApiAuthenticationError:
            _LOGGER.debug("Authentication failed during data fetch, attempting re-login")
            await self._async_refresh_auth()
            api_response = await api_wrapper(
                self._session,
                method="get",
                url=self.connection_url,
                headers=self._build_headers(),
                data={},
            )

        _LOGGER.debug(
            "Return API Status:%s ",
            api_response["status"],
        )

        if api_response["status"] == 0:
            patients = sorted(api_response["data"], key=lambda x: x["patientId"])
        else:
            patients = api_response

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
        api_response = await api_wrapper(
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
            api_response,
        )

        return api_response


class LibreLinkApiLogin:
    """API class to retrieve token."""

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

    async def async_get_token(self) -> dict:
        """Get token and account ID from the API."""
        response_login = await api_wrapper(
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
            response_login["status"],
        )
        if response_login["status"] == 2:
            raise LibreLinkApiAuthenticationError(
                "Invalid credentials",
            )

        token = response_login["data"]["authTicket"]["token"]
        account_id = response_login["data"]["user"]["id"]

        return {"token": token, "accountId": account_id}


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
            return await response.json()

    except asyncio.TimeoutError as exception:
        raise LibreLinkApiCommunicationError(
            "Timeout error fetching information",
        ) from exception
    except (aiohttp.ClientError, socket.gaierror) as exception:
        raise LibreLinkApiCommunicationError(
            "Error fetching information",
        ) from exception
    except LibreLinkApiAuthenticationError:
        raise
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
