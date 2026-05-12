# evcc - Minimum Current Automation

Minimum current is changed depending on if a loadpoint is charging with 1 or 3 phases.
This is helpful for vehicles which need a certain minimum current to charge properly, like the Renault Twingo.

You probably want to set up the script as a systemd service, e.g. if you use it on a Raspberry Pi.

[mqtt](https://docs.evcc.io/docs/reference/configuration/mqtt) must be configured in evcc.

## Resilience

Script now:
- retries first MQTT connection forever
- reconnects automatically after disconnect
- survives callback errors
- keeps trying if MQTT loop crashes unexpectedly

Systemd unit now:
- starts only after network-online
- restarts process always
- waits 5s before restart

## Optional environment variables

- `MQTT_BROKER` (default: `localhost`)
- `MQTT_BROKER_PORT` (default: `1883`)
- `MQTT_KEEPALIVE_SECONDS` (default: `60`)
- `MQTT_RECONNECT_MIN_DELAY_SECONDS` (default: `1`)
- `MQTT_RECONNECT_MAX_DELAY_SECONDS` (default: `60`)
- `MIN_CURRENT_1_PHASE` (default: `6`)
- `MIN_CURRENT_3_PHASES` (default: `8`)
- `LOG_LEVEL` (default: `INFO`)
