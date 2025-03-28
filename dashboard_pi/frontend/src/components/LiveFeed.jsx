import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { BACKEND_BASE_URL } from "../config";

const LiveFeed = () => {
  const [imageSrc, setImageSrc] = useState("");

  useEffect(() => {
    const socket = io(BACKEND_BASE_URL);

    // Listen for "live_feed" events from the backend
    socket.on("live_feed", (payload) => {
      // Expect payload to be an object with an "image" property
      if (payload && payload.image) {
        setImageSrc(`data:image/jpeg;base64,${payload.image}`);
      }
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Live Video Feed</h2>
      {/* Updated height to 600px for a larger live feed box */}
      <div className="w-full h-[600px] bg-gray-300 flex items-center justify-center">
        {imageSrc ? (
          <img src={imageSrc} alt="Live Feed" className="w-full h-full object-cover" />
        ) : (
          <p>Waiting for feed...</p>
        )}
      </div>
    </div>
  );
};

export default LiveFeed;