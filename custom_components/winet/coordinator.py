"""Coordinator che legge lo stato della stufa."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WinetApi, WinetError
from .const import STATUS_KEYS

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class WinetData:
    """Dati normalizzati di un ciclo di polling."""

    status_code: int
    status_key: str
    flue_temperature: float | None
    room_temperature: float | None
    target_temperature: float | None
    power: int
    fan: int
    signal: int | None
    num_power: int
    set_temp_div: float
    device_name: str
    raw: dict[str, Any] = field(default_factory=dict)


def _as_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_params(params: Any) -> dict[int, Any]:
    result: dict[int, Any] = {}
    if not isinstance(params, list):
        return result
    for item in params:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        register = _as_int(item[0], -1)
        if register >= 0:
            result[register] = item[1]
    return result


class WinetCoordinator(DataUpdateCoordinator[WinetData]):
    """Legge /api/global + registro 020 e combina i valori."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: WinetApi,
        name: str,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> WinetData:
        try:
            global_data, detail = await asyncio.gather(
                self.api.async_get_global(),
                self.api.async_get_detail(),
            )
        except WinetError as err:
            raise UpdateFailed(str(err)) from err

        params = _parse_params(detail.get("params"))

        temp_div = _as_float(detail.get("tempDiv"), 0.5) or 0.5
        set_temp_div = _as_float(detail.get("setTempDiv"), 1.0) or 1.0

        status_code = _as_int(params.get(2), 0)
        air_raw = params.get(0)
        set_raw = params.get(50)

        room_temperature = (
            round(float(air_raw) * temp_div, 1)
            if air_raw is not None
            else _as_float(global_data.get("air"))
        )
        target_temperature = (
            round(float(set_raw) * set_temp_div, 1)
            if set_raw is not None
            else None
        )

        return WinetData(
            status_code=status_code,
            status_key=STATUS_KEYS.get(status_code, "unknown"),
            flue_temperature=_as_float(global_data.get("gasflue")),
            room_temperature=room_temperature,
            target_temperature=target_temperature,
            power=_as_int(params.get(51), _as_int(global_data.get("power"), 0)),
            fan=_as_int(params.get(47), 0),
            signal=_as_int(detail.get("signal"), 0),
            num_power=max(_as_int(detail.get("numPower"), 5), 1),
            set_temp_div=set_temp_div,
            device_name=str(detail.get("name") or ""),
            raw={"global": global_data, "detail": detail},
        )
