CREATE TABLE IF NOT EXISTS remediations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    failure_pattern TEXT NOT NULL,
    resource_title TEXT NOT NULL,
    resource_type TEXT DEFAULT 'article' CHECK(resource_type IN ('article', 'video', 'exercise', 'example', 'documentation')),
    resource_url TEXT,
    resource_content TEXT,
    difficulty_level TEXT DEFAULT 'beginner' CHECK(difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    language TEXT DEFAULT 'python',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_remediations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    remediation_id INTEGER NOT NULL,
    submission_id INTEGER,
    is_viewed BOOLEAN DEFAULT 0,
    is_completed BOOLEAN DEFAULT 0,
    recommended_at TEXT DEFAULT CURRENT_TIMESTAMP,
    viewed_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (remediation_id) REFERENCES remediations(id),
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

CREATE INDEX IF NOT EXISTS idx_remediations_pattern ON remediations(failure_pattern);
CREATE INDEX IF NOT EXISTS idx_student_remediations_student ON student_remediations(student_id);
CREATE INDEX IF NOT EXISTS idx_student_remediations_remediation ON student_remediations(remediation_id);

INSERT OR IGNORE INTO remediations (id, failure_pattern, resource_title, resource_type, resource_url, resource_content, difficulty_level, language)
VALUES 
    (1, 'syntax_error', 'Python Syntax Basics', 'article', 'https://docs.python.org/3/tutorial/introduction.html', 'Review basic Python syntax including indentation, colons, and parentheses.', 'beginner', 'python'),
    (2, 'name_error', 'Understanding Variable Scope', 'article', 'https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces', 'Learn about variable scope and how to properly define variables before use.', 'beginner', 'python'),
    (3, 'type_error', 'Python Type System', 'article', 'https://docs.python.org/3/library/stdtypes.html', 'Understand Python data types and type conversion.', 'beginner', 'python'),
    (4, 'index_error', 'Working with Lists and Indices', 'article', 'https://docs.python.org/3/tutorial/introduction.html#lists', 'Learn about list indexing and avoiding out-of-bounds errors.', 'beginner', 'python'),
    (5, 'infinite_loop', 'Loop Control Best Practices', 'article', 'https://docs.python.org/3/tutorial/controlflow.html', 'Review loop conditions and how to prevent infinite loops.', 'intermediate', 'python'),
    (6, 'timeout', 'Algorithm Efficiency', 'article', 'https://wiki.python.org/moin/TimeComplexity', 'Optimize your code for better performance.', 'intermediate', 'python'),
    (7, 'runtime_error', 'Debugging Python Programs', 'article', 'https://docs.python.org/3/library/pdb.html', 'Learn debugging techniques to find and fix runtime errors.', 'intermediate', 'python'),
    (8, 'assertion_error', 'Understanding Assertions', 'article', 'https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement', 'Learn how assertions work and what assertion errors mean.', 'beginner', 'python');
