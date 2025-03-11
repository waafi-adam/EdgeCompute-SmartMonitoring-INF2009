import paho.mqtt.client as mqtt
from mqtt_config import BROKER_IP, BROKER_PORT

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code:", rc)
    client.subscribe("ai_alerts")

def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")

# Initialize MQTT client
client = mqtt.Client("AnalyticsPiProcessor")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKER_PORT, 60)
client.loop_forever()
