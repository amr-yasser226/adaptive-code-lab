CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO settings (key, value) VALUES ('app_name', 'ACCL Lab');
INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance_mode', 'false');