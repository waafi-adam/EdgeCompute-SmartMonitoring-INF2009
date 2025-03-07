import React from "react";

const UserModal = ({ isOpen, onClose, user, onSave, handleInputChange, handleFileChange, handleTogglePresent }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-lg w-11/12 md:w-3/4 lg:w-1/2 max-w-3xl relative">
        <h2 className="text-xl font-bold mb-4">{user.id ? "Edit User" : "Add User"}</h2>
        <input
          type="text"
          name="name"
          placeholder="Enter name"
          value={user.name}
          onChange={handleInputChange}
          className="border p-2 rounded w-full mb-2"
          required
        />
        <button
          onClick={handleTogglePresent}
          className={`border p-2 rounded w-full mb-2 ${
            user.isPresent ? "bg-green-500 text-white" : "bg-red-500 text-white"
          }`}
        >
          {user.isPresent ? "Present" : "Away"}
        </button>
        <input
          type="text"
          name="role"
          placeholder="Enter role"
          value={user.role}
          onChange={handleInputChange}
          className="border p-2 rounded w-full mb-2"
        />
        <input
          type="text"
          name="phone"
          placeholder="Enter phone number (optional)"
          value={user.phone}
          onChange={handleInputChange}
          className="border p-2 rounded w-full mb-2"
        />
        <input
          type="email"
          name="email"
          placeholder="Enter email (optional)"
          value={user.email}
          onChange={handleInputChange}
          className="border p-2 rounded w-full mb-2"
        />
        <label className="block text-sm mb-1">Upload Photo (optional)</label>
        <input type="file" name="photo" accept="image/*" onChange={handleFileChange} className="border p-2 rounded w-full mb-2" />
        <label className="block text-sm mb-1">Upload Voice Sample (optional)</label>
        <input type="file" name="voice" accept="audio/*" onChange={handleFileChange} className="border p-2 rounded w-full mb-2" />
        <div className="flex justify-end mt-4">
          <button onClick={onClose} className="bg-gray-500 text-white px-4 py-2 rounded mr-2">Cancel</button>
          <button onClick={onSave} className="bg-blue-500 text-white px-4 py-2 rounded">Save</button>
        </div>
      </div>
    </div>
  );
};

export default UserModal;
