import json
from datetime import datetime
from mqtt.mqtt_config import MQTT_GESTURE_ALERT_TOPIC

def publish_gesture_alert(client, gesture_name):
    payload = json.dumps({
        "timestamp": datetime.now().isoformat(),
        "message": gesture_name
    })
    client.publish(MQTT_GESTURE_ALERT_TOPIC, payload)
