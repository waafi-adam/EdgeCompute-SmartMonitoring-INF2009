import mqtt from "mqtt";
import { Server } from "socket.io";
import { getLocalIP } from "../utils/networkUtils.js";  // ✅ Use modularized function

const LOCAL_IP = getLocalIP();
const MQTT_BROKER = `mqtt://${LOCAL_IP}`;  // ✅ Use dynamically obtained IP
const MQTT_TOPIC = "live_feed";

// Initialize WebSocket
let ioInstance;
export const setupSocket = (io) => {
  ioInstance = io;
};

// Initialize MQTT Client
const client = mqtt.connect(MQTT_BROKER);

client.on("connect", () => {
  console.log(`✅ Connected to MQTT Broker at ${MQTT_BROKER}`);
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
