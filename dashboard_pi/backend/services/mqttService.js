import mqtt from "mqtt";
import { getLocalIP } from "../utils/networkUtils.js";

const LOCAL_IP = getLocalIP();
const MQTT_BROKER = `mqtt://${LOCAL_IP}`;
const MQTT_FEED_TOPIC = "live_feed";

// Initialize WebSocket instance
let ioInstance;

export const setupSocket = (io) => {
  ioInstance = io;
};

// Initialize MQTT Client
const client = mqtt.connect(MQTT_BROKER);

client.on("connect", () => {
  console.log(`? Connected to MQTT Broker at ${MQTT_BROKER}`);

  // Subscribe to video feed
  client.subscribe(MQTT_FEED_TOPIC, (err) => {
    if (err) {
      console.error("Error subscribing to live_feed:", err);
    }
  });

    // Subscribe to all alert topics
    const alertTopics = ["alerts/face", "alerts/object", "alerts/gesture", "alerts/voice"];
  alertTopics.forEach((topic) => {
    client.subscribe(topic, (err) => {
      if (err) {
        console.error(`Error subscribing to ${topic}:`, err);
      }
    });
  });
});

client.on("message", (topic, message) => {
  try {
    const payload = JSON.parse(message.toString());

    console.log(`[MQTT] Message on topic ${topic}:`, payload);

    if (ioInstance) {
      if (topic === MQTT_FEED_TOPIC) {
        ioInstance.emit("live_feed", payload);
      } else if (
        topic === "alerts/face" ||
        topic === "alerts/object" ||
        topic === "alerts/gesture" ||
        topic === "alerts/voice"
      ) {
        ioInstance.emit("alert", payload);
      }      
    }
  } catch (err) {
    console.error("Error parsing MQTT message:", err);
  }
});