"""Climate per la stufa WiNET."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WinetError
from .const import CONF_TEMP_SENSOR, DOMAIN, HEATING_CODES
from .coordinator import WinetCoordinator
from .entity import WinetEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WinetCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WinetClimate(coordinator, entry)])


class WinetClimate(WinetEntity, ClimateEntity):
    """Termostato della stufa."""

    _attr_name = None
    _attr_translation_key = "stove"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 5
    _attr_max_temp = 40

    def __init__(self, coordinator: WinetCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "climate")

    @property
    def _temp_sensor(self) -> str | None:
        return self._entry.options.get(CONF_TEMP_SENSOR) or None

    @property
    def target_temperature_step(self) -> float:
        return self.coordinator.data.set_temp_div or 1.0

    @property
    def current_temperature(self) -> float | None:
        sensor = self._temp_sensor
        if sensor:
            state = self.hass.states.get(sensor)
            if state and state.state not in ("unknown", "unavailable", ""):
                try:
                    return float(state.state)
                except (TypeError, ValueError):
                    pass
        return self.coordinator.data.room_temperature

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data.target_temperature

    @property
    def hvac_mode(self) -> HVACMode:
        return (
            HVACMode.OFF
            if self.coordinator.data.status_code == 0
            else HVACMode.HEAT
        )

    @property
    def hvac_action(self) -> HVACAction:
        code = self.coordinator.data.status_code
        if code == 0:
            return HVACAction.OFF
        if code in HEATING_CODES:
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "status_code": data.status_code,
            "status_key": data.status_key,
            "module_name": data.device_name,
            "host": self.coordinator.api.host,
            "temperature_sensor": self._temp_sensor,
        }

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        try:
            await self.coordinator.api.async_set_status(hvac_mode == HVACMode.HEAT)
        except WinetError as err:
            raise HomeAssistantError(f"Comando stufa non riuscito: {err}") from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        try:
            await self.coordinator.api.async_set_temperature(float(temperature))
        except WinetError as err:
            raise HomeAssistantError(f"Setpoint non impostato: {err}") from err
        await self.coordinator.async_request_refresh()
