"""Custom types for click4food_integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import Click4FoodApiClient
    from .coordinator import Click4FoodDataUpdateCoordinator


type Click4FoodConfigEntry = ConfigEntry[Click4FoodData]


@dataclass
class Click4FoodData:
    """Data for the Click4Food integration."""

    client: Click4FoodApiClient
    coordinator: Click4FoodDataUpdateCoordinator
    integration: Integration
