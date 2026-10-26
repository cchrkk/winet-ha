"""Selezione della velocità ventola."""

from __future__ import annotations

import asyncio

from homeassistant.components.select import SelectEntity
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
    async_add_entities([WinetFanSelect(coordinator, entry)])


class WinetFanSelect(WinetEntity, SelectEntity):
    """Ventola: 0 = auto/off, 1, 2."""

    _attr_translation_key = "fan"
    _attr_options = ["0", "1", "2"]
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "fan")

    @property
    def current_option(self) -> str | None:
        value = str(self.coordinator.data.fan)
        return value if value in self.options else None

    async def async_select_option(self, option: str) -> None:
        speed = int(option)
        try:
            # Sul modulo il passaggio diretto a 2 a volte non viene applicato:
            # si passa da 1 per un paio di secondi, come nella UI originale.
            if speed == 2:
                await self.coordinator.api.async_set_fan(1)
                await asyncio.sleep(2)
            await self.coordinator.api.async_set_fan(speed)
        except (WinetError, ValueError) as err:
            raise HomeAssistantError(f"Ventola non impostata: {err}") from err
        await self.coordinator.async_request_refresh()
