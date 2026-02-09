-- UP
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

-- DOWN
DROP TABLE sessions;
