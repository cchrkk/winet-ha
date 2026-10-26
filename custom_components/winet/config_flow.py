"""Config flow per WiNET."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .api import WinetApi, WinetError
from .const import (
    CONF_HOST,
    CONF_TEMP_SENSOR,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

CONF_SCAN_INTERVAL = "scan_interval"


def _scan_interval_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(
            min=MIN_SCAN_INTERVAL,
            max=MAX_SCAN_INTERVAL,
            step=1,
            mode=NumberSelectorMode.BOX,
            unit_of_measurement="s",
        )
    )


def _temperature_selector() -> EntitySelector:
    return EntitySelector(
        EntitySelectorConfig(domain="sensor", device_class="temperature")
    )


def _base_schema(values: dict[str, Any] | None = None) -> vol.Schema:
    values = values or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST, default=values.get(CONF_HOST, "10.0.0.54")
            ): str,
            vol.Optional(
                CONF_NAME, default=values.get(CONF_NAME, DEFAULT_NAME)
            ): str,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=values.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): _scan_interval_selector(),
            vol.Optional(
                CONF_TEMP_SENSOR,
                description={
                    "suggested_value": values.get(CONF_TEMP_SENSOR)
                },
            ): _temperature_selector(),
        }
    )


def _options_schema(options: dict[str, Any] | None = None) -> vol.Schema:
    options = options or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): _scan_interval_selector(),
            vol.Optional(
                CONF_TEMP_SENSOR,
                description={
                    "suggested_value": options.get(CONF_TEMP_SENSOR)
                },
            ): _temperature_selector(),
        }
    )


class WinetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configurazione iniziale."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            api = WinetApi(async_get_clientsession(self.hass), host, timeout=5)
            try:
                identity = await api.async_get_identity()
            except WinetError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Errore inatteso durante il test del modulo WiNET")
                errors["base"] = "unknown"
            else:
                mac = str(identity.get("mac") or host)
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()
                name = str(user_input.get(CONF_NAME) or DEFAULT_NAME).strip()
                return self.async_create_entry(
                    title=name,
                    data={CONF_HOST: host},
                    options={
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                        CONF_TEMP_SENSOR: user_input.get(CONF_TEMP_SENSOR) or None,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        return WinetOptionsFlow()


class WinetOptionsFlow(OptionsFlow):
    """Opzioni: intervallo e sensore ambiente esterno."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_TEMP_SENSOR] = user_input.get(CONF_TEMP_SENSOR) or None
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(dict(self.config_entry.options)),
        )
