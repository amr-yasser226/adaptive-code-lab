CREATE TABLE IF NOT EXISTS instructors (
    id INTEGER PRIMARY KEY,
    instructor_code TEXT UNIQUE,
    bio TEXT,
    office_hours TEXT,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
