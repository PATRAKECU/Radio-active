-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Simulations table
CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    timestamp TEXT,
    n0 REAL,
    t REAL,
    nt REAL,
    element_id INTEGER,
    name TEXT,
    half_life REAL,
    unit TEXT,
    quantity_unit TEXT
);

-- Radioactive elements table
CREATE TABLE IF NOT EXISTS elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    half_life REAL NOT NULL
);