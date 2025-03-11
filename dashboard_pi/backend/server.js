import express from "express";
import http from "http";
import { Server } from "socket.io";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";
import userRoutes from "./routes/userRoutes.js";
import path from "path";
import os from "os"; // ✅ Import OS module correctly
import { setupSocket } from "./services/mqttService.js";  // Import MQTT handler

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" }
});

setupSocket(io); // Initialize WebSocket

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors({ origin: "*" })); // Allow access from any device on the local network

// Serve static files (uploaded photos/voices)
app.use("/uploads", express.static(path.join(process.cwd(), "uploads")));

// ✅ Fix MongoDB Connection (Remove deprecated options)
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB Connected"))
  .catch(err => console.log("❌ MongoDB Connection Error:", err));

// Use API routes
app.use("/api/users", userRoutes);

// ✅ Get Local Network IP dynamically
function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (let iface in interfaces) {
    for (let config of interfaces[iface]) {
      if (config.family === "IPv4" && !config.internal) {
        return config.address;
      }
    }
  }
  return "localhost"; // Fallback if no network IP found
}

const PORT = process.env.PORT || 5000;
const LOCAL_IP = getLocalIP(); // Get device's local IP dynamically

app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 Server running at http://${LOCAL_IP}:${PORT}`);
});
