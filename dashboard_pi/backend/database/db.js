import sqlite3 from "sqlite3";
import { open } from "sqlite";
import dotenv from "dotenv";

dotenv.config();

const DB_PATH = process.env.SQLITE_DB || "database/smart_monitoring.db";

export async function initDB() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      isPresent BOOLEAN DEFAULT 1,
      role TEXT,
      phone TEXT,
      email TEXT,
      photo TEXT,
      voice TEXT
    );
  `);

  console.log("✅ SQLite database initialized.");
}

export async function getDBConnection() {
  return open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });
}
