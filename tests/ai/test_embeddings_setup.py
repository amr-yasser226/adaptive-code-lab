from infrastructure.database.connection import connect_db
from infrastructure.ai.embeddings import process_submission_embedding

conn = connect_db()
c = conn.cursor()

# Insert a user first
c.execute("""
INSERT INTO users (name, email, password_hash, role, is_active)
VALUES (?, ?, ?, ?, ?)
""", ("Alice", "alice@example.com", "hashed_pw", "student", 1))

user_id = c.lastrowid

# Insert a student referencing the user
c.execute("""
INSERT INTO students (id, student_number, program, YearLevel)
VALUES (?, ?, ?, ?)
""", (user_id, "S1001", "CS", 3))

student_id = user_id

# Insert a course (assuming instructor exists with id=1)
c.execute("""
INSERT INTO courses (instructor_id, code, title, description, year, semester, credits)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (1, "CS101", "Intro to CS", "Description", 2025, "Fall", 3))

course_id = c.lastrowid

# Insert an assignment
c.execute("""
INSERT INTO assignments (course_id, title, description, release_date, due_date)
VALUES (?, ?, ?, DATETIME('now'), DATETIME('now', '+7 days'))
""", (course_id, "Example Assignment", "Description"))

assignment_id = c.lastrowid

# Insert a submission
c.execute("""
INSERT INTO submissions (assignment_id, student_id)
VALUES (?, ?)
""", (assignment_id, student_id))

submission_id = c.lastrowid
conn.commit()
conn.close()

# Now test embedding
process_submission_embedding(submission_id, "def add(a,b): return a+b")