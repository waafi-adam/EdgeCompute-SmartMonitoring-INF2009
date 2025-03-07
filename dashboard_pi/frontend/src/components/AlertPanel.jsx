import React, { useState, useEffect } from "react";

const dummyAlerts = [
  { id: 1, message: "Unrecognized face detected", time: "2 mins ago" },
  { id: 2, message: "Object detected: Suspicious package", time: "5 mins ago" },
];

const AlertPanel = () => {
  const [alerts, setAlerts] = useState(dummyAlerts);

  useEffect(() => {
    const interval = setInterval(() => {
      const newAlert = {
        id: alerts.length + 1,
        message: "New security alert triggered!",
        time: "Just now",
      };
      setAlerts((prevAlerts) => [newAlert, ...prevAlerts]);
    }, 10000);
    return () => clearInterval(interval);
  }, [alerts]);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Alert Panel</h2>
      <div className="h-60 overflow-y-auto">
        <ul>
          {alerts.map((alert) => (
            <li key={alert.id} className="border-b py-2">
              {alert.message} <span className="text-gray-500 text-sm">({alert.time})</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AlertPanel;
