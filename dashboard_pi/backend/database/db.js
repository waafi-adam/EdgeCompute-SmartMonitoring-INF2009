import Database from "better-sqlite3";
import dotenv from "dotenv";

dotenv.config();

const DB_PATH = process.env.SQLITE_DB || "database/smart_monitoring.db";

// Initialize SQLite Database
const db = new Database(DB_PATH);
db.pragma("journal_mode = WAL"); // Improves performance

// Ensure users table exists
db.exec(`
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

export default db;
