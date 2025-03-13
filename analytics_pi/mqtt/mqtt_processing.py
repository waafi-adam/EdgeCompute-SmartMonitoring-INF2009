import paho.mqtt.client as mqtt
import json
from mqtt_config import BROKER_IP, BROKER_PORT, BROKER_TOPIC_AI_ALERTS  

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code:", rc)
    client.subscribe(BROKER_TOPIC_AI_ALERTS)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"🚨 Threat Alert: {data}")

# Initialize MQTT client
client = mqtt.Client("AnalyticsPiProcessor")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKER_PORT, 60)
client.loop_forever()
