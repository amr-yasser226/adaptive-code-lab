
import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from infrastructure.database.connection import DatabaseManager

# Setup DB Path (Force default for this test)
db_path = os.path.join(os.path.dirname(__file__), '../data/Accl_DB.db')
print(f"Seeding DB at: {db_path}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Clean relevant tables (Optional, but safer for re-runs)
c.execute("DELETE FROM test_cases WHERE id = 9999")
c.execute("DELETE FROM assignments WHERE id = 9999")
c.execute("DELETE FROM courses WHERE id = 9999")
c.execute("DELETE FROM instructors WHERE id = 9998")
c.execute("DELETE FROM enrollments WHERE student_id = 9999")
c.execute("DELETE FROM users WHERE email IN ('student_e2e@test.com', 'inst_e2e@test.com')")

conn.commit()

# 2. Create Users
# Instructor
c.execute("""
    INSERT INTO users (id, name, email, password_hash, role, is_active)
    VALUES (9998, 'E2E Instructor', 'inst_e2e@test.com', ?, 'instructor', 1)
""", (generate_password_hash('password'),))

# Student
c.execute("""
    INSERT INTO users (id, name, email, password_hash, role, is_active)
    VALUES (9999, 'E2E Student', 'student_e2e@test.com', ?, 'student', 1)
""", (generate_password_hash('password'),))

# 3. Create Instructor Profile
c.execute("""
    INSERT INTO instructors (id, instructor_code, bio, office_hours)
    VALUES (9998, 'INST_E2E', 'E2E Bio', 'Always')
""")

# 4. Create Course
c.execute("""
    INSERT INTO courses (id, title, code, description, instructor_id, status, year, semester, credits)
    VALUES (9999, 'E2E Testing Course', 'E2E101', 'Course for Browser Test', 9998, 'active', 2025, 'Spring', 4)
""")

# 5. Enroll Student
c.execute("""
    INSERT INTO enrollments (student_id, course_id, status, enrolled_at)
    VALUES (9999, 9999, 'enrolled', CURRENT_TIMESTAMP)
""")

# 6. Create Assignment
c.execute("""
    INSERT INTO assignments (id, course_id, title, description, max_points, is_published, due_date, created_at)
    VALUES (9999, 9999, 'E2E Assignment', 'Write code that prints "Hello E2E"', 100, 1, '2026-01-01 00:00:00', CURRENT_TIMESTAMP)
""")

# 7. Create Test Case
c.execute("""
    INSERT INTO test_cases (id, assignment_id, name, stdin, expected_out, points, is_visible)
    VALUES (9999, 9999, 'Print Hello', '', 'Hello E2E', 100, 1)
""")

conn.commit()
conn.close()
print("E2E Data Seeded Successfully.")
