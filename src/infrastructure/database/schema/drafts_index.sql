-- Index to speed up cleanup by updated_at
CREATE INDEX IF NOT EXISTS idx_drafts_updated_at ON drafts(updated_at);
