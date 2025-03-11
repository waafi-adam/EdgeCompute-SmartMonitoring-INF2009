import threading
from mqtt.mqtt_live_feed import client as live_feed_client
from mqtt.mqtt_processing import client as processing_client

# Start live feed streaming
live_feed_thread = threading.Thread(target=live_feed_client.loop_forever)
processing_thread = threading.Thread(target=processing_client.loop_forever)

live_feed_thread.start()
processing_thread.start()
