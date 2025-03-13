import threading
from mqtt.mqtt_live_feed import start_live_feed
from mqtt.mqtt_processing import client as processing_client
from ai_models.object_detection import detect_threats

def start_mqtt_processing():
    processing_client.loop_forever()

def start_ai_models():
    detect_threats()

# Start all modules in parallel
live_feed_thread = threading.Thread(target=start_live_feed)
processing_thread = threading.Thread(target=start_mqtt_processing)
ai_models_thread = threading.Thread(target=start_ai_models)

live_feed_thread.start()
processing_thread.start()
ai_models_thread.start()

live_feed_thread.join()
processing_thread.join()
ai_models_thread.join()
