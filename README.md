# WiNET Stove — Home Assistant integration

Custom HACS integration for pellet stoves with the **WiNET** module from
Net Software / StufaSmart, driven through the module's **local API**: no cloud.

## Entities

A single device exposing:

| Entity | Purpose |
|---|---|
| `climate.stove` | on/off, target temperature, current temperature (external sensor or stove probe) |
| `sensor.stove_phase` | detailed phase: waiting for flame, ignition, running, stand-by, final cleaning, brazier cleaning, alarm |
| `sensor.stove_flue` | flue temperature |
| `sensor.stove_air` | temperature read by the stove probe |
| `sensor.stove_setpoint` | configured setpoint |
| `sensor.stove_wifi_signal` | module signal (diagnostic) |
| `number.stove_power` | power 1..N (N read from the module) |
| `select.stove_fan` | fan 0/1/2 |
| `binary_sensor.stove_alarm` | alarm or alarm memory |

Entity IDs are derived from the device name chosen during setup, so the examples
above use `stove`; with the default name in Italian they become `climate.stufa`,
`sensor.stufa_fase`, and so on.

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → **Custom repositories**
2. Repository URL, category **Integration**, add
3. Install **WiNET Stove**
4. Restart Home Assistant
5. Settings → Devices & services → **Add integration** → *WiNET Stove*
6. Enter the module IP (for example `10.0.0.54`)

### Manual

Copy `custom_components/winet` to `<config>/custom_components/winet` and restart.

`deploy.ps1` copies the integration to a Windows/SMB config share and keeps a
backup of the previous version.

## Options

- **Update interval**: default 10 s (min 5, max 300)
- **Room temperature sensor**: when set, `climate` uses it as
  `current_temperature`. Recommended: the stove probe measures the air next to
  the stove, not the room.

## API used

- `GET /api/id` — identity (MAC used as unique_id)
- `GET /api/global` — flue temperature, power, coarse state
- `POST /ajax/get-registers` `key=020&category=2` — detailed register
- `POST /api/status/1|0`, `POST /api/power/N`, `POST /api/temperature/air/T`
  (T in **half degrees**: 25 °C = `50`)
- `POST /ajax/set-register` `key=002&memory=1&regId=47&value=N` — fan

The local API has no authentication: keep the module on a trusted network.

## Notes

- The stove setpoint is scaled with `setTempDiv`, the air temperature with
  `tempDiv`, both read from the register: no hard-coded `/2`.
- The phase uses register 2 (0–9), not the coarse `/api/global` state, which
  loses ignition, running and stand-by.
- The alarm is a separate `binary_sensor`: it does not imply an empty hopper.
- `climate.turn_off` really turns the stove off: use it only when needed.

## License

MIT.

---

Italiano: [README.it.md](README.it.md)
