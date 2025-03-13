import express from "express";
import db from "../database/db.js";

const router = express.Router();

// ✅ Get all alerts
router.get("/", (req, res) => {
    try {
        const alerts = db.prepare("SELECT * FROM alerts ORDER BY timestamp DESC").all();
        res.json(alerts);
    } catch (err) {
        res.status(500).json({ error: "Failed to retrieve alerts" });
    }
});

export default router;
