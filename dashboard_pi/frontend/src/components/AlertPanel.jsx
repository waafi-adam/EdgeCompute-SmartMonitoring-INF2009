import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import axios from "axios";
import { BACKEND_BASE_URL } from "../config";

const socket = io(BACKEND_BASE_URL);

const AlertPanel = () => {
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        fetchAlerts();  // ✅ Load past alerts when component loads
        socket.on("new_alert", (alertData) => {
            setAlerts((prevAlerts) => [alertData, ...prevAlerts]);  // ✅ Real-time update
        });

        return () => {
            socket.off("new_alert");
        };
    }, []);

    const fetchAlerts = async () => {
        try {
            const res = await axios.get(`${BACKEND_BASE_URL}/api/alerts`);
            setAlerts(res.data);
        } catch (err) {
            console.error("Error fetching alerts:", err);
        }
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Threat Alerts</h2>
            <div className="h-60 overflow-y-auto">
                <ul>
                    {alerts.map((alert, index) => (
                        <li key={index} className="border-b py-2">
                            <strong>⚠️ Threat Detected:</strong> {alert.objects}
                            <br />
                            <small className="text-gray-500">
                                {new Date(alert.timestamp * 1000).toLocaleTimeString()}
                            </small>
                            <br />
                            <img src={alert.image} alt="Threat Image" className="mt-2 w-40 h-auto rounded" />
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default AlertPanel;
