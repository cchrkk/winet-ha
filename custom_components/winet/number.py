"""Numero per la potenza della stufa."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WinetError
from .const import DOMAIN
from .coordinator import WinetCoordinator
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WinetCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WinetPowerNumber(coordinator, entry)])


class WinetPowerNumber(WinetEntity, NumberEntity):
    """Potenza di lavoro 1..N."""

    _attr_translation_key = "power"
    _attr_native_min_value = 1
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power")

    @property
    def native_max_value(self) -> float:
        return float(self.coordinator.data.num_power)

    @property
    def native_value(self) -> float:
        return float(self.coordinator.data.power)

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.coordinator.api.async_set_power(int(value))
        except WinetError as err:
            raise HomeAssistantError(f"Potenza non impostata: {err}") from err
        await self.coordinator.async_request_refresh()
