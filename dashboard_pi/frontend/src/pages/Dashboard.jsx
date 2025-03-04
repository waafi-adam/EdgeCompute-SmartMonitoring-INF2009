import React from "react";
import LiveFeed from "../components/LiveFeed";
import AlertPanel from "../components/AlertPanel";
import UserManagement from "../components/UserManagement";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <h1 className="text-3xl font-bold text-center mb-6">Smart Monitoring Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <LiveFeed />
        <AlertPanel />
      </div>
      <div className="mt-6">
        <UserManagement />
      </div>
    </div>
  );
};

export default Dashboard;
