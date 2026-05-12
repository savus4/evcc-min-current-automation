import paho.mqtt.client as mqtt
import logging
import os
import time

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration (env vars optional).
mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
mqtt_broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
min_current_1_phase = int(os.getenv("MIN_CURRENT_1_PHASE", "6"))
min_current_3_phases = int(os.getenv("MIN_CURRENT_3_PHASES", "8"))
keepalive_seconds = int(os.getenv("MQTT_KEEPALIVE_SECONDS", "60"))
reconnect_min_delay = int(os.getenv("MQTT_RECONNECT_MIN_DELAY_SECONDS", "1"))
reconnect_max_delay = int(os.getenv("MQTT_RECONNECT_MAX_DELAY_SECONDS", "60"))

# evcc topics
min_current_topic = "evcc/loadpoints/1/minCurrent"
phases_configured_topic = "evcc/loadpoints/1/phasesConfigured"

if reconnect_min_delay < 1:
    reconnect_min_delay = 1
if reconnect_max_delay < reconnect_min_delay:
    reconnect_max_delay = reconnect_min_delay


def on_connect(client, userdata, flags, rc, properties):
    logger.info("Connected with result code %s", rc)
    client.subscribe(min_current_topic)
    client.subscribe(phases_configured_topic)
    logger.info("Subscribed to evcc topics.")

last_configured_phase = None


def on_disconnect(client, userdata, flags, rc, properties):
    if rc == 0:
        logger.info("Disconnected cleanly.")
    else:
        logger.warning("Disconnected unexpectedly (rc=%s). Reconnecting...", rc)


def publish_min_current(client, value):
    topic = f"{min_current_topic}/set"
    info = client.publish(topic, str(value))
    info.wait_for_publish(timeout=5)
    if info.rc == mqtt.MQTT_ERR_SUCCESS:
        logger.info("Changed minCurrent to %sA.", value)
    else:
        logger.warning("Publish failed on %s (rc=%s).", topic, info.rc)


def on_message(client, userdata, msg):
    global last_configured_phase

    if msg.topic != phases_configured_topic:
        return

    try:
        phase = msg.payload.decode().strip()
    except UnicodeDecodeError:
        logger.warning("Cannot decode payload on %s: %r", msg.topic, msg.payload)
        return

    if phase == "1" and last_configured_phase != "1":
        publish_min_current(client, min_current_1_phase)
        last_configured_phase = "1"
    elif phase == "3" and last_configured_phase != "3":
        publish_min_current(client, min_current_3_phases)
        last_configured_phase = "3"
    elif phase not in {"1", "3"}:
        logger.warning("Unexpected phase payload on %s: %r", msg.topic, phase)


def create_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=reconnect_min_delay, max_delay=reconnect_max_delay)
    client.suppress_exceptions = True
    client.enable_logger(logger)
    return client


def run():
    logger.info(
        "Starting MQTT automation broker=%s port=%s keepalive=%s",
        mqtt_broker,
        mqtt_broker_port,
        keepalive_seconds,
    )
    logger.info(
        "Configured min current: 1-phase=%sA, 3-phases=%sA",
        min_current_1_phase,
        min_current_3_phases,
    )
    client = create_client()
    client.connect_async(mqtt_broker, mqtt_broker_port, keepalive_seconds)
    while True:
        try:
            client.loop_forever(retry_first_connection=True)
            logger.warning("MQTT loop stopped unexpectedly. Restarting loop in 5s.")
        except Exception:
            logger.exception("MQTT loop crashed. Restarting loop in 5s.")
        time.sleep(5)


if __name__ == "__main__":
    run()
