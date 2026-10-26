"""Selezione della velocità ventola."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WinetError
from .const import CONF_FAN_SPEEDS, DEFAULT_FAN_SPEEDS, DOMAIN
from .coordinator import WinetCoordinator
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WinetCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WinetFanSelect(coordinator, entry)])


class WinetFanSelect(WinetEntity, SelectEntity):
    """Ventola: 0 = spenta, poi 1..N velocità."""

    _attr_translation_key = "fan"
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "fan")

    @property
    def _fan_speeds(self) -> int:
        try:
            return int(
                self._entry.options.get(CONF_FAN_SPEEDS, DEFAULT_FAN_SPEEDS)
            )
        except (TypeError, ValueError):
            return DEFAULT_FAN_SPEEDS

    @property
    def options(self) -> list[str]:
        return [str(speed) for speed in range(self._fan_speeds + 1)]

    @property
    def current_option(self) -> str | None:
        value = str(self.coordinator.data.fan)
        return value if value in self.options else None

    async def async_select_option(self, option: str) -> None:
        try:
            await self.coordinator.api.async_set_fan(int(option))
        except (WinetError, ValueError) as err:
            raise HomeAssistantError(f"Ventola non impostata: {err}") from err
        await self.coordinator.async_request_refresh()
