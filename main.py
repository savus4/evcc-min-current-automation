import paho.mqtt.client as mqtt
import logging

# Change these values. No authentication supported at this point.
mqtt_broker = "localhost"
mqtt_broker_port = 1883
min_current_1_phase = 6
min_current_3_phases = 8

# evcc topics
min_current_topic = "evcc/loadpoints/1/minCurrent"
phases_configured_topic = "evcc/loadpoints/1/phasesActive"

logging.basicConfig(level=logging.INFO)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))
    client.subscribe(min_current_topic)
    client.subscribe(phases_configured_topic)

last_configured_phase = None

def on_message(client, userdata, msg):
    global last_configured_phase

    if msg.topic == phases_configured_topic:
        if msg.payload.decode() == "1" and last_configured_phase != "1":
            client.publish(f"{min_current_topic}/set", f"{min_current_1_phase}")
            logging.info(f"Changed minCurrent to {min_current_1_phase}A.")
            last_configured_phase = "1"
        elif msg.payload.decode() == "3" and last_configured_phase != "3":
            client.publish(f"{min_current_topic}/set", f"{min_current_3_phases}")
            logging.info(f"Changed minCurrent to {min_current_3_phases}A.")
            last_configured_phase = "3"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_broker_port, 60)
client.loop_forever()
