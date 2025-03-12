import fs from "fs";
import path from "path";
import {
  getAllUsers as fetchUsers,
  getUserById,
  createUser as createUserModel,
  updateUser as updateUserModel,
  deleteUser as deleteUserModel,
  deleteAllUsers as deleteAllUsersModel
} from "../models/UserModel.js";

// Get all users
export const getAllUsers = (req, res) => {
  try {
    const users = fetchUsers();
    const formattedUsers = users.map(user => ({ ...user, _id: user.id }));
    res.json(formattedUsers);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Create a new user
export const createUser = (req, res) => {
  try {
    const { name, isPresent, role, phone, email } = req.body;
    const photo = req.files?.photo ? `/uploads/${req.files.photo[0].filename}` : null;
    const voice = req.files?.voice ? `/uploads/${req.files.voice[0].filename}` : null;

    const newUser = createUserModel({ name, isPresent, role, phone, email, photo, voice });

    res.status(201).json(newUser);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

// Update a user
export const updateUser = (req, res) => {
  try {
    const { name, isPresent, role, phone, email } = req.body;
    const id = req.params.id;

    const existingUser = getUserById(id);
    if (!existingUser) return res.status(404).json({ error: "User not found" });

    let photo = existingUser.photo;
    let voice = existingUser.voice;

    if (req.files?.photo) {
      if (photo) fs.unlinkSync(path.join(process.cwd(), photo));
      photo = `/uploads/${req.files.photo[0].filename}`;
    }

    if (req.files?.voice) {
      if (voice) fs.unlinkSync(path.join(process.cwd(), voice));
      voice = `/uploads/${req.files.voice[0].filename}`;
    }

    const updatedUser = updateUserModel(id, { name, isPresent, role, phone, email, photo, voice });

    res.json(updatedUser);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

// Delete a user
export const deleteUser = (req, res) => {
  try {
    const id = req.params.id;
    const existingUser = getUserById(id);
    if (!existingUser) return res.status(404).json({ error: "User not found" });

    if (existingUser.photo) fs.unlinkSync(path.join(process.cwd(), existingUser.photo));
    if (existingUser.voice) fs.unlinkSync(path.join(process.cwd(), existingUser.voice));

    deleteUserModel(id);

    res.json({ message: "User deleted successfully" });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

// Delete all users
export const deleteAllUsers = (req, res) => {
  try {
    // Delete all user files before removing users from the database
    const users = fetchUsers();
    users.forEach(user => {
      if (user.photo) {
        const photoPath = path.join(process.cwd(), user.photo);
        if (fs.existsSync(photoPath)) fs.unlinkSync(photoPath);
      }
      if (user.voice) {
        const voicePath = path.join(process.cwd(), user.voice);
        if (fs.existsSync(voicePath)) fs.unlinkSync(voicePath);
      }
    });

    // Now delete all users from the database
    deleteAllUsersModel();

    res.json({ message: "⚠️ All users and associated files have been deleted!" });
  } catch (err) {
    console.error("Error deleting all users:", err);
    res.status(400).json({ error: err.message });
  }
};

