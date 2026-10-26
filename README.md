# WiNET Stove — integrazione Home Assistant

Integrazione custom (HACS) per le stufe a pellet con modulo **WiNET** di Net
Software / StufaSmart, pilotata dalle **API locali** del modulo: niente cloud.

## Cosa crea

Un device unico con:

| Entità | Cosa fa |
|---|---|
| `climate.stufa` | on/off, setpoint, temperatura corrente (da sensore esterno o sonda stufa) |
| `sensor.stufa_fase` | fase dettagliata: attesa fiamma, accensione, lavoro, stand-by, pulizia finale, pulizia braciere, allarme |
| `sensor.stufa_fumi` | temperatura fumi |
| `sensor.stufa_aria` | temperatura letta dalla sonda della stufa |
| `sensor.stufa_setpoint` | setpoint impostato |
| `sensor.stufa_segnale_wifi` | segnale del modulo (diagnostica) |
| `number.stufa_potenza` | potenza 1..N (N letto dal modulo) |
| `select.stufa_ventola` | ventola 0/1/2 |
| `binary_sensor.stufa_allarme` | allarme o memoria allarme |

## Installazione

### HACS (repository custom)

1. HACS → Integrations → menu ⋮ → **Custom repositories**
2. URL del repo, categoria **Integration**, Aggiungi
3. Installa **WiNET Stove**
4. Riavvia Home Assistant
5. Impostazioni → Dispositivi e servizi → **Aggiungi integrazione** → *WiNET Stove*
6. IP: `10.0.0.54` (o quello del modulo)

### Manuale

Copia `custom_components/winet` in `<config>/custom_components/winet` e riavvia.

Lo script `deploy.ps1` copia l'integrazione su `\\10.0.0.85\config` con backup
della versione precedente.

## Opzioni

- **Intervallo di aggiornamento**: default 10 s (min 5, max 300)
- **Sensore temperatura ambiente**: se impostato, `climate` usa quello come
  `current_temperature`. Consigliato: la stufa è in corridoio e la sua sonda
  misura l'aria vicino alla stufa, non la casa.

## API usate

- `GET /api/id` — identità (MAC per l'unique_id)
- `GET /api/global` — fumi, potenza, stato sintetico
- `POST /ajax/get-registers` `key=020&category=2` — registro dettagliato
- `POST /api/status/1|0`, `POST /api/power/N`, `POST /api/temperature/air/T`
  (T in **mezzi gradi**: 25 °C = `50`)
- `POST /ajax/set-register` `key=002&memory=1&regId=47&value=N` — ventola

Le API locali non hanno autenticazione: il modulo va tenuto su una rete fidata.

## Note

- Il setpoint della stufa viene scalato con `setTempDiv`, la temperatura aria con
  `tempDiv`, letti dal registro: niente `/2` fisso.
- La fase usa il codice del registro 2 (0–9), non lo stato sintetico di
  `/api/global` che perde accensione, lavoro e stand-by.
- L'allarme è un `binary_sensor` separato: non implica "vasca vuota".
- `climate.turn_off` spegne davvero la stufa: usarlo solo quando serve.

## Licenza

MIT.
