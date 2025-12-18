(-- Drafts table for autosave/draft recovery
CREATE TABLE IF NOT EXISTS drafts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	assignment_id INTEGER NOT NULL,
	content TEXT NOT NULL,
	metadata TEXT,
	version INTEGER NOT NULL DEFAULT 1,
	created_at DATETIME DEFAULT (datetime('now')),
	updated_at DATETIME DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_drafts_user_assignment ON drafts(user_id, assignment_id);
)
