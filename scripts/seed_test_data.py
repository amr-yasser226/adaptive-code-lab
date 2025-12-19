import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime, timedelta

def seed_test_data():
    db_path = Path(__file__).parent.parent / 'data' / 'Accl_DB.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    password_hash = generate_password_hash('testpassword123')
    
    print("=== Seeding Test Data ===\n")
    
    # 1. Create demo instructor with entry in instructors table
    print("Creating demo instructor...")
    cursor.execute('SELECT id FROM users WHERE email = ?', ('demo_instructor@accl.edu',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', ('Demo Instructor', 'demo_instructor@accl.edu', password_hash, 'instructor', 1))
        instructor_id = cursor.lastrowid
        
        # Also add to instructors table for full functionality
        cursor.execute('''
            INSERT OR IGNORE INTO instructors (id, instructor_code, bio, office_hours)
            VALUES (?, ?, ?, ?)
        ''', (instructor_id, 'DEMO001', 'Demo instructor for testing', 'Mon-Fri 9-5'))
        print(f"  Created instructor ID: {instructor_id}")
    else:
        print("  Demo instructor already exists")
        cursor.execute('SELECT id FROM users WHERE email = ?', ('demo_instructor@accl.edu',))
        instructor_id = cursor.fetchone()[0]
    
    # 2. Create demo student
    print("Creating demo student...")
    cursor.execute('SELECT id FROM users WHERE email = ?', ('demo_student@accl.edu',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', ('Demo Student', 'demo_student@accl.edu', password_hash, 'student', 1))
        student_id = cursor.lastrowid
        print(f"  Created student ID: {student_id}")
    else:
        cursor.execute('SELECT id FROM users WHERE email = ?', ('demo_student@accl.edu',))
        student_id = cursor.fetchone()[0]
        print("  Demo student already exists")
    
    # 3. Create course for demo instructor
    print("Creating demo course...")
    cursor.execute('SELECT id FROM courses WHERE code = ?', ('DEMO101',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO courses (code, title, description, instructor_id, year, semester, max_students, credits, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', ('DEMO101', 'Demo Programming Course', 'A course for testing instructor features', 
              instructor_id, '2024', 'Fall', 30, 3, 'active'))
        course_id = cursor.lastrowid
        print(f"  Created course ID: {course_id}")
    else:
        cursor.execute('SELECT id FROM courses WHERE code = ?', ('DEMO101',))
        course_id = cursor.fetchone()[0]
        print("  Demo course already exists")
    
    # 4. Create assignment for demo course
    print("Creating demo assignment...")
    cursor.execute('SELECT id FROM assignments WHERE title = ? AND course_id = ?', ('Demo Assignment', course_id))
    if not cursor.fetchone():
        due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        release_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO assignments (course_id, title, description, release_date, due_date, max_points, is_published, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (course_id, 'Demo Assignment', 'Test assignment for instructor testing', release_date, due_date, 100, 1))
        assignment_id = cursor.lastrowid
        print(f"  Created assignment ID: {assignment_id}")
    else:
        cursor.execute('SELECT id FROM assignments WHERE title = ? AND course_id = ?', ('Demo Assignment', course_id))
        assignment_id = cursor.fetchone()[0]
        print("  Demo assignment already exists")
    
    # 5. Enroll student in course
    print("Enrolling demo student in course...")
    cursor.execute('SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?', (student_id, course_id))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO enrollments (student_id, course_id, status, enrolled_at)
            VALUES (?, ?, ?, datetime('now'))
        ''', (student_id, course_id, 'enrolled'))
        print("  Enrolled student in course")
    else:
        print("  Student already enrolled")
    
    # 6. Create test submission
    print("Creating demo submission...")
    cursor.execute('SELECT id FROM submissions WHERE student_id = ? AND assignment_id = ?', (student_id, assignment_id))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO submissions (student_id, assignment_id, code, status, score, submitted_at, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (student_id, assignment_id, 'print("Hello, World!")', 'graded', 85))
        submission_id = cursor.lastrowid
        print(f"  Created submission ID: {submission_id}")
    else:
        print("  Demo submission already exists")
    
    conn.commit()
    conn.close()
    
    print("\n=== Test Data Seeding Complete ===")
    print("\nTest Accounts:")
    print("  Instructor: demo_instructor@accl.edu / testpassword123")
    print("  Student: demo_student@accl.edu / testpassword123")
    print(f"\nDemo Course: DEMO101 (ID: {course_id})")
    print(f"Demo Assignment: Demo Assignment (ID: {assignment_id})")

if __name__ == '__main__':
    seed_test_data()
