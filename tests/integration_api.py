import unittest
import os
import shutil
import tempfile
import sqlite3
import json
import io
import sys
from werkzeug.security import generate_password_hash

# Ensure we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Set ENV for DB path before importing app
temp_dir = tempfile.mkdtemp()
temp_db_path = os.path.join(temp_dir, 'test_db.db')
original_db_path = os.path.join(os.path.dirname(__file__), '../data/Accl_DB.db')

# Copy existing DB schema/data to temp
shutil.copy2(original_db_path, temp_db_path)
os.environ['ACCL_DB_PATH'] = temp_db_path

from web.app import create_app
from infrastructure.database.connection import DatabaseManager

class TestApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app({'TESTING': True, 'WTF_CSRF_ENABLED': False})
        cls.client = cls.app.test_client()
        cls.db_path = temp_db_path
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(temp_dir)

    def setUp(self):
        # Reuse the connection from the App to avoid locking issues
        # Access user_repo to get the db connection
        with self.app.app_context():
            user_repo = self.app.extensions['services']['user_repo']
            self.conn = user_repo.db
            self.cursor = self.conn.cursor()
            
            # 1. Create Instructor User
            self.cursor.execute("INSERT OR IGNORE INTO users (id, name, email, password_hash, role) VALUES (999, 'Test Inst', 'inst@test.com', ?, 'instructor')", (generate_password_hash('password'),))
            
            # 1b. Create Instructor Profile
            self.cursor.execute("INSERT OR IGNORE INTO instructors (id, instructor_code, bio, office_hours) VALUES (999, 'INST001', 'Bio', 'Mon-Fri')")
            
            # 2. Create Course
            self.cursor.execute("""
                INSERT OR IGNORE INTO courses (id, title, code, description, instructor_id, status, year, semester, credits) 
                VALUES (999, 'Test Course', 'TC101', 'Desc', 999, 'active', 2024, 'Fall', 3)
            """)
            
            # 3. Create Assignment
            self.cursor.execute("""
                INSERT OR IGNORE INTO assignments (id, course_id, title, description, max_points, is_published, created_at, updated_at, due_date) 
                VALUES (999, 999, 'Test Assign', 'Desc', 100, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            
            # 4. Create Test Case
            self.cursor.execute("""
                INSERT OR IGNORE INTO test_cases (id, assignment_id, name, stdin, expected_out, points, is_visible) 
                VALUES (999, 999, 'Simple Addition', '1 2', '3', 10, 1)
            """)
            
            self.conn.commit()
            # Do NOT close self.conn as it belongs to the app services

    def tearDown(self):
        pass

    def login(self, email, password):
        return self.client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

    def test_code_execution_success(self):
        self.login('inst@test.com', 'password')
        
        # Correct Python code
        code = """
import sys
parts = sys.stdin.read().split()
a = int(parts[0])
b = int(parts[1])
print(a + b)
"""
        response = self.client.post('/api/test-code', json={
            'code': code,
            'assignment_id': 999,
            'language': 'python'
        })
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['score'], 100.0)
        self.assertEqual(len(data['test_results']), 1)
        self.assertTrue(data['test_results'][0]['passed'])

    def test_code_execution_failure(self):
        self.login('inst@test.com', 'password')
        
        # Incorrect code
        code = """
print("Wrong")
"""
        response = self.client.post('/api/test-code', json={
            'code': code,
            'assignment_id': 999,
            'language': 'python'
        })
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['score'], 0.0)
        self.assertFalse(data['test_results'][0]['passed'])

    def test_syntax_error(self):
        self.login('inst@test.com', 'password')
        
        # Syntax check dry run (if no test cases) - wait, we have test cases.
        # But if code has syntax error, it fails inside exec too.
        code = """
def broken_function(
"""
        response = self.client.post('/api/test-code', json={
            'code': code,
            'assignment_id': 999,
            'language': 'python'
        })
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertFalse(data['test_results'][0]['passed'])
        self.assertIn("Error", data['test_results'][0]['output'])

if __name__ == '__main__':
    unittest.main()
