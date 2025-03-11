import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { BACKEND_BASE_URL } from "../config";

const LiveFeed = () => {
  const [imageSrc, setImageSrc] = useState("");

  useEffect(() => {
    const socket = io(BACKEND_BASE_URL);

    socket.on("live_feed", (imageData) => {
      setImageSrc(`data:image/jpeg;base64,${imageData}`);
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Live Video Feed</h2>
      <div className="w-full h-60 bg-gray-300 flex items-center justify-center">
        {imageSrc ? <img src={imageSrc} alt="Live Feed" className="w-full h-full object-cover" /> : <p>🔴 Waiting for feed...</p>}
      </div>
    </div>
  );
};

export default LiveFeed;
