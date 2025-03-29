import paho.mqtt.client as mqtt

# Configuration constants
MQTT_BROKER = "dashboard-pi.local"  # Use your Dashboard Pi's hostname (or IP)
MQTT_PORT = 1883
MQTT_FEED_TOPIC = "live_feed"
MQTT_ALERT_TOPIC = "alerts"
MQTT_FACE_ALERT_TOPIC = "alerts/face"
MQTT_OBJECT_ALERT_TOPIC = "alerts/object"
MQTT_GESTURE_ALERT_TOPIC = "alerts/gesture"
MQTT_VOICE_ALERT_TOPIC = "alerts/voice"

def connect_mqtt():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    return client