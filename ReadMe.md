# evcc - Minimum Current Automation

Minimum current is changed depending on if a loadpoint is charging with 1 or 3 phases.
This is helpful for vehicles which need a certain minimum current to charge properly, like the Renault Twingo.

You probably want to set up the script as a systemd service, e.g. if you use it on a Raspberry Pi.

[mqtt](https://docs.evcc.io/docs/reference/configuration/mqtt) must be configured in evcc.