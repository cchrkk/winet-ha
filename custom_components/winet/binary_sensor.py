"""Binary sensor per allarmi."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ALARM_CODES, DOMAIN
from .coordinator import WinetCoordinator
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WinetCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WinetAlarmSensor(coordinator, entry)])


class WinetAlarmSensor(WinetEntity, BinarySensorEntity):
    """ON quando la stufa è in allarme o in memoria allarme."""

    _attr_translation_key = "alarm"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "alarm")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.status_code in ALARM_CODES

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "code": self.coordinator.data.status_code,
            "status_key": self.coordinator.data.status_key,
        }
