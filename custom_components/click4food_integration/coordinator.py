"""DataUpdateCoordinator for click4food_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    Click4FoodApiClientAuthenticationError,
    Click4FoodApiClientError,
)

if TYPE_CHECKING:
    from .data import Click4FoodConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class Click4FoodDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: Click4FoodConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except Click4FoodApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except Click4FoodApiClientError as exception:
            raise UpdateFailed(exception) from exception

    @property
    def running_total(self) -> str | None:
        """Return the running total from the data."""
        qry_details = self.data.get("QRYDETAILSGROUPED", [])
        if qry_details and "KEY" in qry_details[0]:
            return qry_details[0]["KEY"].get("RUNNING_TOTAL", "No Data")
        return "No Data"
