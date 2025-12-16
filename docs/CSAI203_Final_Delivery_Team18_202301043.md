# CSAI203 Phase 5 Documentation
## Adaptive Collaborative Code Learning Lab (ACCL)

**Team 18 | Representative ID: 202301043**

---

## Table of Contents
1. [Testing Documentation](#1-testing-documentation)
2. [User Documentation](#2-user-documentation)
3. [Technical Documentation](#3-technical-documentation)

---

## 1. Testing Documentation

### 1.1 Test Suite Overview

The ACCL project maintains a comprehensive test suite with **412 automated tests** achieving **66% code coverage**.

| Test Category | Count | Description |
|--------------|-------|-------------|
| Unit Tests | ~350 | Service and repository tests |
| Integration Tests | ~50 | End-to-end route tests |
| Security Tests | ~8 | Authentication and authorization |
| Performance Tests | ~4 | Response time benchmarks |

### 1.2 Running Tests

**Prerequisites:**
```bash
source .venv/bin/activate
```

**Commands:**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/security/ -v

# Run with verbose output
pytest tests/ -v --tb=short
```

### 1.3 Unit Test Coverage

| Component | Coverage | Key Tests |
|-----------|----------|-----------|
| AuthService | 90% | Login, register, password hashing |
| StudentService | 85% | Submit assignment, enroll, GPA |
| InstructorService | 88% | Create course/assignment, export |
| AssignmentService | 92% | CRUD operations, visibility |
| SimilarityService | 75% | Plagiarism detection |

### 1.4 Manual Testing

**Test Cases (Sample):**

1. **User Registration Flow**
   - Navigate to `/auth/register`
   - Enter valid name, email, password
   - Verify redirect to login page
   - Login with new credentials

2. **Assignment Submission Flow**
   - Login as student
   - Navigate to assignment
   - Submit Python code
   - Verify test results display

3. **Instructor Analytics**
   - Login as instructor
   - Navigate to analytics dashboard
   - Verify real data displays
   - Export CSV and verify contents

### 1.5 CI/CD Automated Testing

GitHub Actions runs on every push/PR:
- Python 3.12 environment setup
- Dependency installation
- pytest execution with coverage
- Docker image build

---

## 2. User Documentation

### 2.1 Installation

**System Requirements:**
- Python 3.12 or higher
- 512MB RAM minimum
- 100MB disk space

**Installation Steps:**

```bash
# 1. Clone repository
git clone https://github.com/your-repo/adaptive-code-lab.git
cd adaptive-code-lab

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 2.2 Running the Application

**Development Server:**
```bash
python run.py
```

**Docker Deployment:**
```bash
docker-compose up --build
```

Access at: **http://localhost:5000**

### 2.3 User Roles

| Role | Capabilities |
|------|-------------|
| Student | View assignments, submit code, view results, request hints |
| Instructor | Create assignments, view analytics, export grades, review plagiarism |
| Admin | Manage users, system configuration |

### 2.4 Basic Usage Guide

**For Students:**
1. Log in with your credentials
2. View available assignments on Dashboard
3. Click on an assignment to view details
4. Write/paste code in the submission editor
5. Click "Test" to run tests locally
6. Click "Submit" to submit for grading
7. View results and AI-generated hints

**For Instructors:**
1. Log in with instructor credentials
2. Access Analytics from the navigation
3. View class performance statistics
4. Export grades as CSV
5. Review plagiarism flags

---

## 3. Technical Documentation

### 3.1 Architecture Overview

ACCL follows the **Clean Architecture** pattern with **MVC** structure:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│              (Flask Routes, Templates, API)              │
├─────────────────────────────────────────────────────────┤
│                    Application Layer                     │
│                      (Services)                          │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                         │
│                      (Entities)                          │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│           (Repositories, Database, AI Providers)         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 MVC Implementation

| Component | Location | Responsibility |
|-----------|----------|----------------|
| **Model** | `src/core/entities/` | Domain objects (User, Assignment, Submission) |
| **View** | `src/web/templates/` | Jinja2 HTML templates |
| **Controller** | `src/web/routes/` | Flask route handlers |

### 3.3 Database Schema

**Database:** SQLite via SQLAlchemy ORM

**Core Tables:**

| Table | Description | Key Fields |
|-------|-------------|------------|
| `users` | All user accounts | id, name, email, password_hash, role |
| `students` | Student-specific data | user_id, student_code, gpa |
| `instructors` | Instructor-specific data | user_id, instructor_code, bio |
| `courses` | Course information | id, instructor_id, code, title |
| `assignments` | Assignment definitions | id, course_id, title, due_date |
| `test_cases` | Test case definitions | id, assignment_id, stdin, expected_out |
| `submissions` | Student code submissions | id, student_id, assignment_id, score |
| `results` | Per-test results | id, submission_id, test_case_id, passed |
| `similarity_flags` | Plagiarism detection | id, submission_id, similarity_score |

### 3.4 Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Authenticate user |
| `/auth/register` | POST | Register new user |
| `/api/test-code` | POST | Execute code tests |
| `/api/assignment/<id>/test-cases` | GET | Get test cases |
| `/instructor/analytics/export` | GET | Export grades CSV |

### 3.5 Design Patterns Used

1. **Repository Pattern** - Data access abstraction
2. **Factory Pattern** - Flask app factory (`create_app`)
3. **Service Layer** - Business logic separation
4. **Dependency Injection** - Service container

### 3.6 Assumptions

1. Users have reliable internet connectivity
2. Python code submissions only (for sandbox execution)
3. SQLite sufficient for demo/course use (no high concurrency)
4. AI providers (Groq/Gemini) available for hint generation
5. Single-tenant deployment (no multi-organization support)

---

## Appendix: Non-Functional Requirements Testing

| Requirement | Test Method | Result |
|-------------|-------------|--------|
| **Security** - Password hashing | Unit test checks bcrypt/pbkdf2 | ✓ Pass |
| **Performance** - Response time < 2s | Integration test timing | ✓ Pass |
| **Usability** - Mobile responsive | Manual browser testing | ✓ Pass |
| **Reliability** - Error handling | Exception tests | ✓ Pass |

---

*Document Version: 1.0 | Date: December 2025*
