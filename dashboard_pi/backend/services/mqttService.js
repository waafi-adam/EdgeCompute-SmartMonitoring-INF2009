import mqtt from "mqtt";
import fs from "fs";
import path from "path";
import { Server } from "socket.io";
import db from "../database/db.js";
import { getLocalIP } from "../utils/networkUtils.js"; // ✅ Use modularized function

const LOCAL_IP = getLocalIP();
const MQTT_BROKER = `mqtt://${LOCAL_IP}`;

// MQTT Topics
const LIVE_FEED_TOPIC = "live_feed";
const ALERT_TOPIC = "ai_alerts";

// Alert storage directory
const ALERT_DIR = "uploads/alerts/";
if (!fs.existsSync(ALERT_DIR)) {
    fs.mkdirSync(ALERT_DIR, { recursive: true });
}

let ioInstance;
export const setupSocket = (io) => {
    ioInstance = io;
};

// Initialize MQTT Client
const client = mqtt.connect(MQTT_BROKER);

client.on("connect", () => {
    console.log(`✅ Connected to MQTT Broker at ${MQTT_BROKER}`);
    client.subscribe(LIVE_FEED_TOPIC);
    client.subscribe(ALERT_TOPIC);
});

client.on("message", (topic, message) => {
    if (topic === LIVE_FEED_TOPIC) {
        const imageData = message.toString();
        // Broadcast live feed to frontend
        if (ioInstance) {
            ioInstance.emit("live_feed", imageData);
        }
    } else if (topic === ALERT_TOPIC) {
        const alertData = JSON.parse(message.toString());
        const imagePath = saveAlertImage(alertData.image);

        const newAlert = {
            timestamp: alertData.timestamp,
            objects: alertData.objects.join(", "),
            image: imagePath
        };

        // ✅ Save alert to database
        saveAlertToDB(newAlert);

        // ✅ Send alert to frontend
        if (ioInstance) {
            ioInstance.emit("new_alert", newAlert);
        }
    }
});

// Save alert image to `uploads/alerts/`
function saveAlertImage(base64String) {
    const filename = `${Date.now()}.jpg`;
    const filepath = path.join(ALERT_DIR, filename);
    fs.writeFileSync(filepath, Buffer.from(base64String, "base64"));
    return `/uploads/alerts/${filename}`;
}

// ✅ Save alert to SQLite database
function saveAlertToDB(alert) {
    db.prepare(`
        INSERT INTO alerts (timestamp, objects, image) 
        VALUES (?, ?, ?)
    `).run(alert.timestamp, alert.objects, alert.image);
}
