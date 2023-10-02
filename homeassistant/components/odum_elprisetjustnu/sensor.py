"""Support for ElprisetJustNu sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CURRENT_PRICE,
    DAY_AVERAGE_PRICE,
    DOMAIN,
    UNIT_OF_M_PRICE,
    VAL_CURRENT_PRICE,
    VAL_DAY_AVERAGE_PRICE,
)
from .coordinator import FetchPriceCoordinator


@dataclass
class ElprisetJustNuDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], StateType]
    extra_state_attributes_fn: Callable[[Any], dict[str, str]] | None
    elpriset_default_measurement: str


@dataclass
class ElprisetJustNuEntityDescription(
    SensorEntityDescription, ElprisetJustNuDescriptionMixin
):
    """Describes sensor entity."""

    # value_fn=lambda data: data.get(VAL_CURRENT_PRICE),


SENSOR_TYPES: tuple[ElprisetJustNuEntityDescription, ...] = (
    ElprisetJustNuEntityDescription(
        key=CURRENT_PRICE,
        icon="mdi:cash-clock",
        state_class=None,
        device_class=SensorDeviceClass.MONETARY,
        value_fn=lambda data: data.get(VAL_CURRENT_PRICE),
        extra_state_attributes_fn=None,
        elpriset_default_measurement=UNIT_OF_M_PRICE,
        # extra_state_attributes_fn=lambda data: {
        #     ATTR_DESCR: data[ATTR_API_AQI_DESCRIPTION],
        #     ATTR_LEVEL: data[ATTR_API_AQI_LEVEL],
        # },
    ),
    ElprisetJustNuEntityDescription(
        key=DAY_AVERAGE_PRICE,
        icon="mdi:cash-clock",
        state_class=None,
        device_class=SensorDeviceClass.MONETARY,
        value_fn=lambda data: data.get(VAL_DAY_AVERAGE_PRICE),
        extra_state_attributes_fn=None,
        elpriset_default_measurement=UNIT_OF_M_PRICE,
        # extra_state_attributes_fn=lambda data: {
        #     ATTR_DESCR: data[ATTR_API_AQI_DESCRIPTION],
        #     ATTR_LEVEL: data[ATTR_API_AQI_LEVEL],
        # },
    ),
    # state_class=SensorStateClass.MEASUREMENT,
)

ATTRIBUTION = "Data provided by ElprisetJustNu"

PARALLEL_UPDATES = 1

ATTR_DESCR = "description"
ATTR_LEVEL = "level"
ATTR_STATION = "reporting_station"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities based on a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # entities = [
    #     ElprisetJustNuSensor(coordinator, description) for description in SENSOR_TYPES
    # ]

    entities = []
    for description in SENSOR_TYPES:
        entities.append(ElprisetJustNuSensor(coordinator, description))

    async_add_entities(entities, False)


class ElprisetJustNuSensor(CoordinatorEntity[FetchPriceCoordinator], SensorEntity):
    """Define sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    entity_description: ElprisetJustNuEntityDescription

    def __init__(
        self,
        coordinator: FetchPriceCoordinator,
        description: ElprisetJustNuEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = description

        # self.unit_of_measurement = description.unit_of_measurement
        # _attr_native_unit_of_measurement = description.unit_of_measurement
        # self.native_unit_of_measurement = description.unit_of_measurement
        self._attr_native_unit_of_measurement = description.elpriset_default_measurement
        if description.key == CURRENT_PRICE:
            self._attr_name = "Current price"
        else:
            self._attr_name = "Average day price"  # + coordinator.price_area

        self._attr_unique_id = (
            description.key.lower() + "_" + coordinator.price_area.lower()
        )

        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the state attributes."""
        if self.entity_description.extra_state_attributes_fn:
            return self.entity_description.extra_state_attributes_fn(
                self.coordinator.data
            )
        return None
