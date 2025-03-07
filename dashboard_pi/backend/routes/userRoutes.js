import express from "express";
import User from "../models/userModel.js";
import multer from "multer";
import path from "path";
import fs from "fs";

const router = express.Router();

// Ensure "uploads" directory exists
const uploadDir = "uploads/";
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Configure Multer to store files with original names
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const upload = multer({ storage });

// Get all users
router.get("/", async (req, res) => {
  try {
    const users = await User.find();
    res.json(users);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Create a new user
router.post("/", upload.fields([{ name: "photo" }, { name: "voice" }]), async (req, res) => {
    try {
      console.log("Received files:", req.files); // Debugging
  
      const { name, isPresent, role, phone, email } = req.body;
      const photo = req.files?.photo ? `/uploads/${req.files.photo[0].filename}` : null;
      const voice = req.files?.voice ? `/uploads/${req.files.voice[0].filename}` : null;
  
      const newUser = new User({ name, isPresent, role, phone, email, photo, voice });
      await newUser.save();
  
      res.status(201).json(newUser);
    } catch (err) {
      console.error("Error saving user:", err);
      res.status(400).json({ error: err.message });
    }
});
  

// Update a user
router.put("/:id", upload.fields([{ name: "photo" }, { name: "voice" }]), async (req, res) => {
    try {
      const { name, isPresent, role, phone, email } = req.body;
      const existingUser = await User.findById(req.params.id);
  
      if (!existingUser) {
        return res.status(404).json({ error: "User not found" });
      }
  
      // Delete old files if a new one is uploaded
      let photo = existingUser.photo;
      let voice = existingUser.voice;
  
      if (req.files?.photo) {
        if (photo) fs.unlinkSync("." + photo); // Delete old photo
        photo = `/uploads/${req.files.photo[0].filename}`;
      }
  
      if (req.files?.voice) {
        if (voice) fs.unlinkSync("." + voice); // Delete old voice
        voice = `/uploads/${req.files.voice[0].filename}`;
      }
  
      const updatedUser = await User.findByIdAndUpdate(
        req.params.id,
        { name, isPresent, role, phone, email, photo, voice },
        { new: true }
      );
  
      res.json(updatedUser);
    } catch (err) {
      console.error("Error updating user:", err);
      res.status(400).json({ error: err.message });
    }
});
  


// Delete a user
router.delete("/:id", async (req, res) => {
    try {
      const user = await User.findById(req.params.id);
  
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }
  
      // Delete the associated photo and voice file
      if (user.photo) fs.unlinkSync("." + user.photo);
      if (user.voice) fs.unlinkSync("." + user.voice);
  
      await User.findByIdAndDelete(req.params.id);
  
      res.json({ message: "User deleted successfully" });
    } catch (err) {
      console.error("Error deleting user:", err);
      res.status(400).json({ error: err.message });
    }
});
  

export default router;
