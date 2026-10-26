"""Client HTTP per il modulo WiNET (API locali)."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class WinetError(Exception):
    """Errore generico del modulo WiNET."""


class WinetConnectionError(WinetError):
    """Il modulo non è raggiungibile."""


class WinetProtocolError(WinetError):
    """Risposta inattesa del modulo."""


class WinetApi:
    """Piccolo client per le API locali del modulo WiNET."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        timeout: float = 6.0,
    ) -> None:
        self._session = session
        self.host = host.strip().rstrip("/")
        if self.host.startswith(("http://", "https://")):
            self.base_url = self.host
        else:
            self.base_url = f"http://{self.host}"
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(
                method, url, timeout=self._timeout, **kwargs
            ) as response:
                if response.status != 200:
                    raise WinetProtocolError(
                        f"{method} {path}: HTTP {response.status}"
                    )
                text = await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise WinetConnectionError(f"{method} {path}: {err}") from err

        try:
            return json.loads(text)
        except ValueError as err:
            raise WinetProtocolError(f"{method} {path}: JSON non valido") from err

    async def async_get_identity(self) -> dict[str, Any]:
        """GET /api/id: identità del modulo."""
        data = await self._request("GET", "/api/id")
        if not isinstance(data, dict):
            raise WinetProtocolError("/api/id: risposta non valida")
        return data

    async def async_get_global(self) -> dict[str, Any]:
        """GET /api/global: stato sintetico della stufa."""
        data = await self._request("GET", "/api/global")
        if not isinstance(data, dict):
            raise WinetProtocolError("/api/global: risposta non valida")
        return data

    async def async_get_detail(self) -> dict[str, Any]:
        """POST /ajax/get-registers (key=020): registro dettagliato."""
        data = await self._request(
            "POST",
            "/ajax/get-registers",
            data={"key": "020", "category": "2"},
        )
        if not isinstance(data, dict):
            raise WinetProtocolError("get-registers: risposta non valida")
        return data

    async def async_get_config(self) -> dict[str, Any]:
        """POST /ajax/get-registers (key=019): configurazione del modulo."""
        data = await self._request(
            "POST",
            "/ajax/get-registers",
            data={"key": "019"},
        )
        if not isinstance(data, dict):
            raise WinetProtocolError("get-registers: risposta non valida")
        return data

    async def async_set_status(self, on: bool) -> None:
        """Accende o spegne la stufa."""
        result = await self._request("POST", f"/api/status/{1 if on else 0}")
        if isinstance(result, dict) and result.get("result") is False:
            raise WinetProtocolError("la stufa ha rifiutato il comando di stato")

    async def async_set_power(self, power: int) -> None:
        """Imposta la potenza di lavoro."""
        result = await self._request("POST", f"/api/power/{int(power)}")
        if isinstance(result, dict) and result.get("result") is False:
            raise WinetProtocolError("la stufa ha rifiutato il comando di potenza")

    async def async_set_temperature(self, temperature: float) -> None:
        """Imposta il setpoint aria.

        L'API locale lavora in mezzi gradi: 25.0 °C si invia come 50.
        """
        value = round(float(temperature) * 2)
        result = await self._request("POST", f"/api/temperature/air/{value}")
        if isinstance(result, dict) and result.get("result") is False:
            raise WinetProtocolError("la stufa ha rifiutato il setpoint")

    async def async_set_fan(self, speed: int) -> None:
        """Imposta la ventola (registro 47)."""
        result = await self._request(
            "POST",
            "/ajax/set-register",
            data={
                "key": "002",
                "memory": "1",
                "regId": "47",
                "value": str(int(speed)),
            },
        )
        if isinstance(result, dict) and result.get("result") is False:
            raise WinetProtocolError("la stufa ha rifiutato la velocità ventola")
