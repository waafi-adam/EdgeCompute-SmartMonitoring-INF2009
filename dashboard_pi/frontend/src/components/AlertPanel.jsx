import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import { BACKEND_BASE_URL } from "../config";

const AlertPanel = () => {
  const [alerts, setAlerts] = useState([]);
  const [initialized, setInitialized] = useState(false);

  // Load saved alerts from localStorage on mount
  useEffect(() => {
    const savedAlerts = localStorage.getItem("alerts");
    console.log("Loaded saved alerts from localStorage:", savedAlerts);
    if (savedAlerts) {
      setAlerts(JSON.parse(savedAlerts));
    }
    setInitialized(true);
  }, []);

  // Persist alerts to localStorage whenever they change, but only after initial load
  useEffect(() => {
    if (initialized) {
      console.log("Saving alerts to localStorage:", alerts);
      localStorage.setItem("alerts", JSON.stringify(alerts));
    }
  }, [alerts, initialized]);

  useEffect(() => {
    const socket = io(BACKEND_BASE_URL);

    socket.on("connect", () => {
      console.log("Socket connected with id:", socket.id);
    });

    // Listen for "alert" events from the backend
    socket.on("alert", (alertData) => {
      console.log("Received alert in AlertPanel:", alertData);
      setAlerts((prevAlerts) => [
        { id: Date.now(), ...alertData },
        ...prevAlerts,
      ]);
    });

    socket.on("disconnect", () => {
      console.log("Socket disconnected");
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Alert Panel</h2>
      <div className="h-60 overflow-y-auto">
        {alerts.length > 0 ? (
          <ul>
            {alerts.map((alert) => (
              <li key={alert.id} className="border-b py-2">
                {alert.message}{" "}
                <span className="text-gray-500 text-sm">
                  ({new Date(alert.timestamp).toLocaleString()})
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No alerts yet.</p>
        )}
      </div>
    </div>
  );
};

export default AlertPanel;
