"""Sample API Client."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

from .const import DATA_PAGE_URL, DATA_URL, LOGGER, LOGIN_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": LOGIN_URL,
    "X-Requested-With": "XMLHttpRequest",
}


class Click4FoodApiClientError(Exception):
    """Exception to indicate a general API error."""


class Click4FoodApiClientCommunicationError(
    Click4FoodApiClientError,
):
    """Exception to indicate a communication error."""


class Click4FoodApiClientAuthenticationError(
    Click4FoodApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise Click4FoodApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


def _verify_jsessionid_or_raise(jsessionid: str | None) -> None:
    """Verify if we have a jsessionid cookie."""
    if jsessionid is None:
        LOGGER.error("JSESSIONID cookie not found after login")
        msg = "Couldn't fetch the JSESSIONID out of the cookie"
        raise Click4FoodApiClientCommunicationError(msg)


def _raise_exception(message: str) -> None:
    """Raise a Click4FoodDataFetchError with the given message."""
    raise Click4FoodApiClientError(message)


class Click4FoodApiClient:
    """Click 4 Food Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Click 4 Food Client."""
        self._username = username
        self._password = password
        self._session = session
        self._jsessionid = None

    async def login(self) -> Any:
        """Login into Click4Food."""
        LOGGER.debug("Login into Click4Food.")

        login_payload = {
            "txtLogin": self._username,
            "txtPassword": self._password,
        }

        try:
            async with self._session.post(
                LOGIN_URL, data=login_payload, headers=HEADERS, allow_redirects=True
            ) as response:
                _verify_response_or_raise(response)

                self._jsessionid = None
                for cookie in self._session.cookie_jar:
                    if cookie.key == "JSESSIONID":
                        self._jsessionid = cookie.value
                        break

                _verify_jsessionid_or_raise(self._jsessionid)
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise Click4FoodApiClientError(
                msg,
            ) from exception

    async def async_get_data(self) -> Any:
        """Fetch the data."""
        if self._jsessionid is None:
            await self.login()

        HEADERS["Cookie"] = f"JSESSIONID={self._jsessionid}"

        client_no, ms_instance_no = await self._fetch_client_details()
        return await self._fetch_data(client_no, ms_instance_no)

    async def _fetch_client_details(self) -> tuple[str, str]:
        """Fetch client and instance details from the HTML page."""
        async with self._session.get(
            DATA_PAGE_URL, headers=HEADERS, allow_redirects=True
        ) as html_response:
            _verify_response_or_raise(html_response)

            html_content = await html_response.text()
            soup = BeautifulSoup(html_content, "html.parser")

            select: Tag | None = soup.find("select", {"id": "client"})
            if not select:
                LOGGER.error("Select element not found in HTML response")
                _raise_exception("Select element not found")

            option: Tag | None = select.find(
                "option", {"value": True, "data-msinstanceno": True}
            )
            if not option:
                LOGGER.error("Client option not found in HTML response")
                _raise_exception("Client option not found")

            client_no: str | None = option.get("value")
            ms_instance_no: str | None = option.get("data-msinstanceno")
            if not client_no or not ms_instance_no:
                LOGGER.error("Required attributes missing in option element")
                _raise_exception("Required attributes missing")

            return client_no, ms_instance_no

    async def _fetch_data(self, client_no: str, ms_instance_no: str) -> Any:
        """Fetch detailed data using the extracted client and instance numbers."""
        today = datetime.now()
        date_until = today.strftime("%Y%m%d")
        date_from = (today - timedelta(days=60)).strftime("%Y%m%d")

        data_payload = {
            "cfc": "ELL.ellClient",
            "method": "GetClientTicketDetails",
            "dateFrom": date_from,
            "dateUntil": date_until,
            "clientNo": client_no,
            "msInstanceNo": ms_instance_no,
        }

        async with self._session.post(
            DATA_URL, data=data_payload, headers=HEADERS, allow_redirects=True
        ) as data_response:
            _verify_response_or_raise(data_response)
            try:
                return json.loads(await data_response.text())
            except json.JSONDecodeError:
                _raise_exception("Invalid JSON format in response")
