import mqtt from "mqtt";
import { Server } from "socket.io";

// MQTT Configuration
const MQTT_BROKER = "mqtt://waafiadam-pi.local";  // Replace with your Dashboard Pi IP
const MQTT_TOPIC = "live_feed";

// Initialize WebSocket
let ioInstance;
export const setupSocket = (io) => {
  ioInstance = io;
};

// Initialize MQTT Client
const client = mqtt.connect(MQTT_BROKER);

client.on("connect", () => {
  console.log("✅ Connected to MQTT Broker");
  client.subscribe(MQTT_TOPIC);
});

client.on("message", (topic, message) => {
  if (topic === MQTT_TOPIC) {
    const imageData = message.toString();
    
    // Broadcast image to WebSocket clients
    if (ioInstance) {
      ioInstance.emit("live_feed", imageData);
    }
  }
});
