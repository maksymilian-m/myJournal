-- Create Users table (SQLITE3)
CREATE TABLE IF NOT EXISTS USERS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weekly_goal INTEGER DEFAULT 0,
    prompts_enabled INTEGER DEFAULT 1
);

-- Create JOURNAL table (SQLITE3)
CREATE TABLE IF NOT EXISTS JOURNAL (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry TEXT NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    word_count INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);

-- Create PROMPTS table (SQLITE3)
CREATE TABLE IF NOT EXISTS PROMPTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);