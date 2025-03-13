import mqtt from "mqtt";
import fs from "fs";
import path from "path";
import { Server } from "socket.io";
import db from "./database/db.js";
import { getLocalIP } from "./utils/networkUtils.js";

const LOCAL_IP = getLocalIP();
const MQTT_BROKER = `mqtt://${LOCAL_IP}`;
const LIVE_FEED_TOPIC = "live_feed";
const ALERT_TOPIC = "ai_alerts";

const ALERT_DIR = "uploads/alerts/";
if (!fs.existsSync(ALERT_DIR)) {
    fs.mkdirSync(ALERT_DIR, { recursive: true });
}

let ioInstance;
export const setupSocket = (io) => {
    ioInstance = io;
};

const client = mqtt.connect(MQTT_BROKER);
client.on("connect", () => {
    console.log(`✅ Connected to MQTT Broker at ${MQTT_BROKER}`);
    client.subscribe(LIVE_FEED_TOPIC);
    client.subscribe(ALERT_TOPIC);
});

client.on("message", (topic, message) => {
    try {
        if (topic === LIVE_FEED_TOPIC) {
            const imageData = message.toString();
            if (ioInstance) {
                ioInstance.emit("live_feed", imageData);
            }
        } else if (topic === ALERT_TOPIC) {
            const alertData = JSON.parse(message.toString());
            const imagePath = saveAlertImage(alertData.image);
            const objects = alertData.objects ? alertData.objects.join(", ") : "Unknown Object";

            const newAlert = { timestamp: alertData.timestamp, objects, image: imagePath };
            saveAlertToDB(newAlert);

            if (ioInstance) {
                ioInstance.emit("new_alert", newAlert);
            }
        }
    } catch (err) {
        console.error("🚨 MQTT ERROR:", err);
    }
});

function saveAlertImage(base64String) {
    const filename = `${Date.now()}.jpg`;
    const filepath = path.join(ALERT_DIR, filename);
    fs.writeFileSync(filepath, Buffer.from(base64String, "base64"));
    return `/uploads/alerts/${filename}`;
}

function saveAlertToDB(alert) {
    db.prepare(`INSERT INTO alerts (timestamp, objects, image) VALUES (?, ?, ?)`).run(alert.timestamp, alert.objects, alert.image);
}
