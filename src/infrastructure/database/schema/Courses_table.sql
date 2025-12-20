-- CREATE TABLE IF NOT EXISTS courses (
--     id INTEGER PRIMARY KEY,
--     instructor_id INTEGER NOT NULL,
--     code TEXT NOT NULL UNIQUE,
--     title TEXT NOT NULL,
--     description TEXT,
--     year INTEGER NOT NULL, 
--     semester TEXT NOT NULL, 
--     max_students INTEGER,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     status TEXT CHECK(status IN ('active', 'inactive','draft')) DEFAULT 'active',
--     updated_at TIMESTAMP,
--     credits INTEGER NOT NULL,
--     FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL
-- );
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instructor_id INTEGER NOT NULL,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    year INTEGER NOT NULL CHECK (year >= 2000),
    semester TEXT NOT NULL CHECK (semester IN ('Fall', 'Spring', 'Summer')),
    max_students INTEGER CHECK (max_students > 0),
    status TEXT NOT NULL
        CHECK (status IN ('draft', 'inactive', 'active'))
        DEFAULT 'draft',
    credits INTEGER NOT NULL CHECK (credits > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
