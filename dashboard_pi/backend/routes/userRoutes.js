import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import {
  getAllUsers,
  createUser,
  updateUser,
  deleteUser
} from "../controllers/userController.js";

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

// Define routes
router.get("/", getAllUsers);
router.post("/", upload.fields([{ name: "photo" }, { name: "voice" }]), createUser);
router.put("/:id", upload.fields([{ name: "photo" }, { name: "voice" }]), updateUser);
router.delete("/:id", deleteUser);

export default router;
