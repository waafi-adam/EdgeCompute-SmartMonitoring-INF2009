import { getDBConnection } from "../database/db.js";

export async function getAllUsers() {
  const db = await getDBConnection();
  return db.all("SELECT * FROM users");
}

export async function createUser(user) {
  const db = await getDBConnection();
  const { name, isPresent, role, phone, email, photo, voice } = user;

  const result = await db.run(
    "INSERT INTO users (name, isPresent, role, phone, email, photo, voice) VALUES (?, ?, ?, ?, ?, ?, ?)",
    [name, isPresent, role, phone, email, photo, voice]
  );

  return { id: result.lastID, ...user };
}

export async function updateUser(id, user) {
  const db = await getDBConnection();
  const { name, isPresent, role, phone, email, photo, voice } = user;

  await db.run(
    "UPDATE users SET name=?, isPresent=?, role=?, phone=?, email=?, photo=?, voice=? WHERE id=?",
    [name, isPresent, role, phone, email, photo, voice, id]
  );

  return { id, ...user };
}

export async function deleteUser(id) {
  const db = await getDBConnection();
  await db.run("DELETE FROM users WHERE id=?", [id]);
}
