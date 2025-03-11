import express from "express";
import http from "http";
import { Server } from "socket.io";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";
import userRoutes from "./routes/userRoutes.js";
import path from "path";
import { getLocalIP } from "./utils/networkUtils.js";  // ✅ Import modularized function
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

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB Connected"))
  .catch(err => console.log("❌ MongoDB Connection Error:", err));

// Use API routes
app.use("/api/users", userRoutes);

const PORT = process.env.PORT || 5000;
const LOCAL_IP = getLocalIP();

server.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 Server running at http://${LOCAL_IP}:${PORT}`);
});
