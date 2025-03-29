import json
from datetime import datetime
from .mqtt_config import MQTT_FEED_TOPIC, MQTT_ALERT_TOPIC

def publish_feed(client, image_base64):
    payload = json.dumps({
        "timestamp": datetime.now().isoformat(),
        "image": image_base64
    })
    client.publish(MQTT_FEED_TOPIC, payload)

def publish_alert(client, message, topic=MQTT_ALERT_TOPIC):
    payload = json.dumps({
        "timestamp": datetime.now().isoformat(),
        "message": message
    })
    client.publish(topic, payload)
