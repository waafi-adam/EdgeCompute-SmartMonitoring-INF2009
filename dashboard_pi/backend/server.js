import express from "express";
import http from "http";
import { Server } from "socket.io";
import cors from "cors";
import dotenv from "dotenv";
import userRoutes from "./routes/userRoutes.js";
import alertRoutes from "./routes/alertRoutes.js"; // ✅ Import alert routes
import path from "path";
import { getLocalIP } from "./utils/networkUtils.js";
import { setupSocket } from "./services/mqttService.js"; 
import db from "./database/db.js";

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

setupSocket(io);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors({ origin: "*" }));

// Serve static files
app.use("/uploads", express.static(path.join(process.cwd(), "uploads")));

// Use API routes
app.use("/api/users", userRoutes);
app.use("/api/alerts", alertRoutes); // ✅ Register alert routes

const PORT = process.env.PORT || 5000;
const LOCAL_IP = getLocalIP();

server.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 Server running at http://${LOCAL_IP}:${PORT}`);
});
