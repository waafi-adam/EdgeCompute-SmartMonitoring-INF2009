const getBackendURL = () => {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:5000`;  // Use the frontend's hostname
  };
  
  export const BACKEND_BASE_URL = `${getBackendURL()}`; // For images and audio files
