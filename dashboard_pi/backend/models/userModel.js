import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  isPresent: { type: Boolean, default: true },
  role: { type: String, required: false },
  phone: { type: String, required: false },
  email: { type: String, required: false },
  photo: { type: String, required: false }, // Stores image URL
  voice: { type: String, required: false }, // Stores audio URL
});

export default mongoose.model("User", userSchema);
