import db from "../database/db.js";

// Get all users
export function getAllUsers() {
  return db.prepare("SELECT * FROM users").all();
}

// Get a user by ID
export function getUserById(id) {
  return db.prepare("SELECT * FROM users WHERE id=?").get(id);
}

// Create a new user
export function createUser({ name, isPresent, role, phone, email, photo, voice }) {
  const stmt = db.prepare(
    "INSERT INTO users (name, isPresent, role, phone, email, photo, voice) VALUES (?, ?, ?, ?, ?, ?, ?)"
  );
  const result = stmt.run(name, isPresent, role, phone, email, photo, voice);
  return { id: result.lastInsertRowid, name, isPresent, role, phone, email, photo, voice };
}

// Update an existing user
export function updateUser(id, { name, isPresent, role, phone, email, photo, voice }) {
  db.prepare(
    "UPDATE users SET name=?, isPresent=?, role=?, phone=?, email=?, photo=?, voice=? WHERE id=?"
  ).run(name, isPresent, role, phone, email, photo, voice, id);
  return { id, name, isPresent, role, phone, email, photo, voice };
}

// Delete a user by ID
export function deleteUser(id) {
  db.prepare("DELETE FROM users WHERE id=?").run(id);
}

// Delete all users
export function deleteAllUsers() {
  db.prepare("DELETE FROM users").run();
}
