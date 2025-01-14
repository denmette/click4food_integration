"""Sensor platform for click4food_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .entity import Click4FoodEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import Click4FoodDataUpdateCoordinator
    from .data import Click4FoodConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="click4food_integration",
        name="Total Amount Left",
        icon="mdi:currency-eur",
        native_unit_of_measurement="€",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: Click4FoodConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        Click4FoodSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class Click4FoodSensor(Click4FoodEntity, SensorEntity):
    """Click4Food Sensor class."""

    def __init__(
        self,
        coordinator: Click4FoodDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.running_total
