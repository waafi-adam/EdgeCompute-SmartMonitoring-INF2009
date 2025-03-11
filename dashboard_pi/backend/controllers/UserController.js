import db from "../database/db.js";
import fs from "fs";
import path from "path";

// Get all users
export const getAllUsers = (req, res) => {
  try {
    const users = db.prepare("SELECT * FROM users").all();
    
    // Ensure frontend gets 'id' instead of '_id'
    const formattedUsers = users.map(user => ({ ...user, _id: user.id }));
    
    res.json(formattedUsers);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};


// Create a new user
export const createUser = (req, res) => {
  try {
    console.log("Received files:", req.files);

    const { name, isPresent, role, phone, email } = req.body;
    const photo = req.files?.photo ? `/uploads/${req.files.photo[0].filename}` : null;
    const voice = req.files?.voice ? `/uploads/${req.files.voice[0].filename}` : null;

    const stmt = db.prepare(
      "INSERT INTO users (name, isPresent, role, phone, email, photo, voice) VALUES (?, ?, ?, ?, ?, ?, ?)"
    );
    const result = stmt.run(name, isPresent, role, phone, email, photo, voice);

    res.status(201).json({ id: result.lastInsertRowid, name, isPresent, role, phone, email, photo, voice });
  } catch (err) {
    console.error("Error saving user:", err);
    res.status(400).json({ error: err.message });
  }
};

// Update a user
export const updateUser = (req, res) => {
  try {
    const { name, isPresent, role, phone, email } = req.body;
    const id = req.params.id;

    // Fetch existing user data
    const existingUser = db.prepare("SELECT photo, voice FROM users WHERE id=?").get(id);
    
    let photo = existingUser.photo;
    let voice = existingUser.voice;

    // Delete old photo if a new one is uploaded
    if (req.files?.photo) {
      if (photo) {
        const oldPhotoPath = path.join(process.cwd(), photo);
        if (fs.existsSync(oldPhotoPath)) {
          fs.unlinkSync(oldPhotoPath); // Delete the old photo
        }
      }
      photo = `/uploads/${req.files.photo[0].filename}`;
    }

    // Delete old voice file if a new one is uploaded
    if (req.files?.voice) {
      if (voice) {
        const oldVoicePath = path.join(process.cwd(), voice);
        if (fs.existsSync(oldVoicePath)) {
          fs.unlinkSync(oldVoicePath); // Delete the old voice file
        }
      }
      voice = `/uploads/${req.files.voice[0].filename}`;
    }

    // Update user in the database
    const stmt = db.prepare(
      "UPDATE users SET name=?, isPresent=?, role=?, phone=?, email=?, photo=?, voice=? WHERE id=?"
    );
    stmt.run(name, isPresent, role, phone, email, photo, voice, id);

    res.json({ id, name, isPresent, role, phone, email, photo, voice });
  } catch (err) {
    console.error("Error updating user:", err);
    res.status(400).json({ error: err.message });
  }
};


// Delete a user
export const deleteUser = (req, res) => {
  try {
    const id = req.params.id;

    // Fetch the user before deleting
    const existingUser = db.prepare("SELECT photo, voice FROM users WHERE id=?").get(id);

    if (existingUser) {
      if (existingUser.photo) {
        const photoPath = path.join(process.cwd(), existingUser.photo);
        if (fs.existsSync(photoPath)) {
          fs.unlinkSync(photoPath); // Delete photo file
        }
      }

      if (existingUser.voice) {
        const voicePath = path.join(process.cwd(), existingUser.voice);
        if (fs.existsSync(voicePath)) {
          fs.unlinkSync(voicePath); // Delete voice file
        }
      }
    }

    // Delete user from database
    db.prepare("DELETE FROM users WHERE id=?").run(id);

    res.json({ message: "User deleted successfully" });
  } catch (err) {
    console.error("Error deleting user:", err);
    res.status(400).json({ error: err.message });
  }
};


export const deleteAllUsers = (req, res) => {
  try {
    db.prepare("DELETE FROM users").run();
    res.json({ message: "⚠️ All users have been deleted!" });
  } catch (err) {
    console.error("Error deleting all users:", err);
    res.status(400).json({ error: err.message });
  }
};