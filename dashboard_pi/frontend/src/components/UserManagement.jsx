import React, { useState } from "react";

const UserManagement = () => {
  const [users, setUsers] = useState([
    { id: 1, name: "John Doe", role: "Household Member" },
    { id: 2, name: "Jane Smith", role: "Guest" },
  ]);
  
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">User Management</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id} className="border-b py-2">
            {user.name} - {user.role}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserManagement;
