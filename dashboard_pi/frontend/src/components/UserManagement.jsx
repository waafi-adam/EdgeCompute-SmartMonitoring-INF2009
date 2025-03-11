import React, { useState, useEffect } from "react";
import axios from "axios";
import UserModal from "./UserModal";

import { BACKEND_BASE_URL } from "../config";

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({
    name: "",
    isPresent: true,
    role: "",
    phone: "",
    email: "",
    photo: null,
    voice: null,
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await axios.get(`${BACKEND_BASE_URL}/api/users`);
      setUsers(res.data);
    } catch (err) {
      console.error("Error fetching users:", err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewUser({ ...newUser, [name]: value });
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    setNewUser({ ...newUser, [name]: files[0] });
  };

  const handleTogglePresent = () => {
    setNewUser({ ...newUser, isPresent: !newUser.isPresent });
  };

  const handleSaveUser = async () => {
    if (!newUser.name) {
      alert("Name is required!");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("name", newUser.name);
      formData.append("isPresent", newUser.isPresent);
      formData.append("role", newUser.role);
      formData.append("phone", newUser.phone);
      formData.append("email", newUser.email);
      if (newUser.photo) formData.append("photo", newUser.photo);
      if (newUser.voice) formData.append("voice", newUser.voice);

      if (editingUser) {
        await axios.put(`${BACKEND_BASE_URL}/api/users/${editingUser._id}`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        });
      } else {
        await axios.post(`${BACKEND_BASE_URL}/api/users`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        });
      }

      fetchUsers();
      setShowModal(false);
      setEditingUser(null);
      setNewUser({ name: "", isPresent: true, role: "", phone: "", email: "", photo: null, voice: null });
    } catch (err) {
      console.error("Error saving user:", err);
    }
  };

  const handleEditUser = (user) => {
    setNewUser(user);
    setEditingUser(user);
    setShowModal(true);
  };

  const handleDeleteUser = async (id) => {
    try {
      await axios.delete(`${BACKEND_BASE_URL}/api/users/${id}`);
      fetchUsers();
    } catch (err) {
      console.error("Error deleting user:", err);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">User Management</h2>
      <button onClick={() => setShowModal(true)} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700 w-full mb-4">
        Add User
      </button>
      <ul className="mt-4 h-60 overflow-y-auto border p-2 rounded">
        {users.map((user) => (
          <li key={user.id} className="border-b py-2 flex justify-between items-center"> {/* Ensure id is used */}
            <div>
              <p><strong>{user.name}</strong> ({user.role || "No Role"})</p>
              {user.phone && <p className="text-sm text-gray-600">📞 {user.phone}</p>}
              {user.email && <p className="text-sm text-gray-600">📧 {user.email}</p>}
              {user.photo && <img src={`${BACKEND_BASE_URL}${user.photo}`} alt="User" className="w-16 h-16 rounded-full object-cover" />}
              {user.voice && (
                <audio controls className="mt-2">
                  <source src={`${BACKEND_BASE_URL}${user.voice}`} type="audio/mp3" />
                  Your browser does not support the audio element.
                </audio>
              )}
            </div>
            <div>
              <button onClick={() => handleEditUser(user)} className="bg-yellow-500 text-white px-2 py-1 rounded mr-2">Edit</button>
              <button onClick={() => handleDeleteUser(user._id)} className="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
            </div>
          </li>
        ))}
      </ul>

      <UserModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        user={newUser}
        onSave={handleSaveUser}
        handleInputChange={handleInputChange}
        handleFileChange={handleFileChange}
        handleTogglePresent={handleTogglePresent}
      />
    </div>
  );
};

export default UserManagement;
