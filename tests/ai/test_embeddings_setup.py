from infrastructure.database.connection import connect_db
from infrastructure.ai.embeddings import process_submission_embedding

def test_embedding_setup():
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

    student_id = user_id

    # Insert an instructor (id=1 for the course constraint)
    # We need a user for the instructor first
    c.execute("""
    INSERT INTO users (name, email, password_hash, role, is_active)
    VALUES (?, ?, ?, ?, ?)
    """, ("Dr. Smith", "smith@example.com", "hashed_pw", "instructor", 1))
    instructor_user_id = c.lastrowid
    
    c.execute("""
    INSERT INTO instructors (id, instructor_code, bio, office_hours)
    VALUES (?, ?, ?, ?)
    """, (instructor_user_id, "INST001", "Bio", "Hours"))
    # Assuming instructor_user_id becomes the instructor_id we refer to (based on common 1:1 schema)
    # But wait, courses.instructor_id refers to instructors.id which refers to users.id
    # We forced course to use 1. If instructor_user_id isn't 1, it will fail.
    # In this isolated test with empty DB, user 1 is Alice. User 2 is Smith.
    # So we should use instructor_user_id for the course.

    # Insert a course
    c.execute("""
    INSERT INTO courses (instructor_id, code, title, description, year, semester, credits)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (instructor_user_id, "CS101", "Intro to CS", "Description", 2025, "Fall", 3))

    if c.lastrowid:
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
        
        # Now test embedding
        process_submission_embedding(submission_id, "def add(a,b): return a+b")
    
    conn.close()