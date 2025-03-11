import db from "../database/db.js";

export function getAllUsers() {
  return db.prepare("SELECT * FROM users").all();
}

export function createUser(user) {
  const { name, isPresent, role, phone, email, photo, voice } = user;
  const result = db
    .prepare("INSERT INTO users (name, isPresent, role, phone, email, photo, voice) VALUES (?, ?, ?, ?, ?, ?, ?)")
    .run(name, isPresent, role, phone, email, photo, voice);

  return { id: result.lastInsertRowid, ...user };
}

export function updateUser(id, user) {
  const { name, isPresent, role, phone, email, photo, voice } = user;
  db.prepare(
    "UPDATE users SET name=?, isPresent=?, role=?, phone=?, email=?, photo=?, voice=? WHERE id=?"
  ).run(name, isPresent, role, phone, email, photo, voice, id);

  return { id, ...user };
}

export function deleteUser(id) {
  db.prepare("DELETE FROM users WHERE id=?").run(id);
}
