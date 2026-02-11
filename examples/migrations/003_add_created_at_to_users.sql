-- UP
ALTER TABLE users ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'));

-- DOWN
ALTER TABLE users DROP COLUMN created_at;
