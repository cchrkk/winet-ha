"""Sensori della stufa WiNET."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, STATUS_KEYS
from .coordinator import WinetCoordinator
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WinetCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WinetPhaseSensor(coordinator, entry),
            WinetFlueSensor(coordinator, entry),
            WinetAirSensor(coordinator, entry),
            WinetSetpointSensor(coordinator, entry),
            WinetWifiSignalSensor(coordinator, entry),
        ]
    )


class WinetPhaseSensor(WinetEntity, SensorEntity):
    """Fase dettagliata (registro 2)."""

    _attr_translation_key = "phase"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(dict.fromkeys([*STATUS_KEYS.values(), "unknown"]))

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "phase")

    @property
    def native_value(self) -> str:
        value = self.coordinator.data.status_key
        return value if value in self.options else "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"code": self.coordinator.data.status_code}

    @property
    def icon(self) -> str:
        return {
            0: "mdi:fire-off",
            1: "mdi:timer-sand",
            2: "mdi:timer-sand",
            3: "mdi:fire-alert",
            4: "mdi:fire",
            5: "mdi:fire-off",
            6: "mdi:broom",
            7: "mdi:broom",
            8: "mdi:alert",
            9: "mdi:alert-outline",
        }.get(self.coordinator.data.status_code, "mdi:help-circle")


class _WinetTemperatureSensor(WinetEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1


class WinetFlueSensor(_WinetTemperatureSensor):
    """Temperatura fumi."""

    _attr_translation_key = "flue"

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "flue")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.flue_temperature


class WinetAirSensor(_WinetTemperatureSensor):
    """Temperatura letta dalla sonda della stufa."""

    _attr_translation_key = "air"

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "air")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.room_temperature


class WinetSetpointSensor(_WinetTemperatureSensor):
    """Setpoint impostato sulla stufa."""

    _attr_translation_key = "setpoint"

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "setpoint")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.target_temperature


class WinetWifiSignalSensor(WinetEntity, SensorEntity):
    """Qualità del segnale Wi-Fi del modulo (barre 0-4)."""

    _attr_translation_key = "wifi_signal"
    _attr_icon = "mdi:wifi"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "wifi_signal")

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.signal
