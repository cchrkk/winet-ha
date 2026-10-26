"""Costanti per l'integrazione WiNET."""

from __future__ import annotations

DOMAIN = "winet"
DEFAULT_NAME = "Stufa"
DEFAULT_SCAN_INTERVAL = 10
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300

CONF_HOST = "host"
CONF_TEMP_SENSOR = "temperature_sensor"

# Codici del registro 2 (key=020, category=2).
STATUS_KEYS: dict[int, str] = {
    0: "off",
    1: "waiting_flame",
    2: "waiting_flame",
    3: "ignition",
    4: "running",
    5: "standby",
    6: "final_cleaning",
    7: "brazier_cleaning",
    8: "alarm",
    9: "alarm_memory",
}

ALARM_CODES = {8, 9}
HEATING_CODES = {1, 2, 3, 4}
