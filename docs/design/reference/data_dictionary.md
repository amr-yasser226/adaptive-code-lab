# USERS

**Description:** Central identity record for all authentication and roles.

| Column        | Type      | Constraints      | Description                          |
| ------------- | --------- | ---------------- | ------------------------------------ |
| id            | int       | PK               | Surrogate primary key                |
| name          | varchar   | NOT NULL         | Full display name                    |
| email         | varchar   | UNIQUE, NOT NULL | Login email; unique identifier       |
| password_hash | varchar   | NOT NULL         | Hashed password                      |
| role          | varchar   | NOT NULL         | User role (student/instructor/admin) |
| created_at    | timestamp | Default now()    | Account creation time                |
| updated_at    | timestamp | —                | Last profile update                  |

**Notes:** Enforce unique email. Consider soft-delete (e.g., deleted_at).

---

# INSTRUCTORS

**Description:** Instructor profile (1:1 with USERS where role = instructor).

| Column          | Type      | Constraints                     | Description                  |
| --------------- | --------- | ------------------------------- | ---------------------------- |
| id              | int       | PK                              | Surrogate key                |
| user_id         | int       | FK → users.id, UNIQUE, NOT NULL | Links to users record        |
| instructor_code | varchar   | UNIQUE                          | Human/legacy instructor code |
| bio             | text      | —                               | Instructor biography         |
| created_at      | timestamp | Default now()                   | Profile creation time        |

**Note:** `user_id` must be unique to enforce 1:1.

---

# STUDENTS

**Description:** Student profile (1:1 with USERS where role = student).

| Column         | Type      | Constraints                     | Description              |
| -------------- | --------- | ------------------------------- | ------------------------ |
| id             | int       | PK                              | Surrogate key            |
| user_id        | int       | FK → users.id, UNIQUE, NOT NULL | Links to users record    |
| student_number | varchar   | UNIQUE, NOT NULL                | Institutional student ID |
| created_at     | timestamp | Default now()                   | Profile creation time    |

**Notes:** `student_number` used for external academic systems.

---

# ADMINS

**Description:** Admin profile (1:1 with USERS where role = admin).

| Column     | Type      | Constraints                     | Description           |
| ---------- | --------- | ------------------------------- | --------------------- |
| id         | int       | PK                              | Surrogate key         |
| user_id    | int       | FK → users.id, UNIQUE, NOT NULL | Links to users record |
| created_at | timestamp | Default now()                   | Profile creation time |

---

# NOTIFICATIONS

**Description:** In-app or system notifications tied to a user.

| Column     | Type      | Constraints             | Description            |
| ---------- | --------- | ----------------------- | ---------------------- |
| id         | int       | PK                      | Notification ID        |
| user_id    | int       | FK → users.id, NOT NULL | Notification recipient |
| message    | text      | NOT NULL                | Notification body      |
| type       | varchar   | —                       | Notification category  |
| is_read    | boolean   | Default false           | Read/unread flag       |
| created_at | timestamp | Default now()           | Creation time          |
| read_at    | timestamp | —                       | Time read              |

**Notes:** Index user_id for fast lookup.

---

# COURSES

**Description:** Courses owned by an instructor.

| Column        | Type      | Constraints                   | Description                |
| ------------- | --------- | ----------------------------- | -------------------------- |
| id            | int       | PK                            | Course ID                  |
| instructor_id | int       | FK → instructors.id, NOT NULL | Course owner               |
| code          | varchar   | UNIQUE, NOT NULL              | Human-readable course code |
| title         | varchar   | NOT NULL                      | Course title               |
| description   | text      | —                             | Long description           |
| status        | varchar   | —                             | Course lifecycle state     |
| created_at    | timestamp | Default now()                 | Creation time              |
| updated_at    | timestamp | —                             | Last update time           |

---

# ENROLLMENTS

**Description:** Student ↔ Course many-to-many relationship.

| Column      | Type      | Constraints                | Description       |
| ----------- | --------- | -------------------------- | ----------------- |
| student_id  | int       | FK → students.id, NOT NULL | Student           |
| course_id   | int       | FK → courses.id, NOT NULL  | Course            |
| enrolled_at | timestamp | Default now()              | Enrollment time   |
| dropped_at  | timestamp | —                          | Drop time         |
| status      | varchar   | —                          | Enrollment status |

**Primary Key:** (student_id, course_id)

---

# ASSIGNMENTS

**Description:** Assignment tasks within a course.

| Column                 | Type      | Constraints               | Description               |
| ---------------------- | --------- | ------------------------- | ------------------------- |
| id                     | int       | PK                        | Assignment ID             |
| course_id              | int       | FK → courses.id, NOT NULL | Owning course             |
| title                  | varchar   | NOT NULL                  | Assignment title          |
| description            | text      | —                         | Full description          |
| release_date           | timestamp | —                         | When available            |
| due_date               | timestamp | NOT NULL                  | Deadline                  |
| max_points             | int       | Default 100               | Maximum points            |
| is_published           | boolean   | Default false             | Visibility                |
| allow_late_submissions | boolean   | Default false             | Late submissions allowed? |
| created_at             | timestamp | Default now()             | Creation time             |
| updated_at             | timestamp | —                         | Last update time          |

---

# TEST_CASES

**Description:** Autograding test cases per assignment.

| Column        | Type      | Constraints                   | Description         |
| ------------- | --------- | ----------------------------- | ------------------- |
| id            | int       | PK                            | Test case ID        |
| assignment_id | int       | FK → assignments.id, NOT NULL | Parent assignment   |
| name          | varchar   | NOT NULL                      | Test case name      |
| stdin         | text      | —                             | Input               |
| expected_out  | text      | NOT NULL                      | Expected output     |
| timeout_ms    | int       | Default 5000                  | Max allowed runtime |
| points        | int       | Default 0                     | Points awarded      |
| is_visible    | boolean   | Default true                  | Visible to student? |
| sort_order    | int       | Default 0                     | Ordering            |
| created_at    | timestamp | Default now()                 | Creation time       |

---

# SUBMISSIONS

**Description:** Student submissions for assignments.

| Column        | Type      | Constraints                   | Description         |
| ------------- | --------- | ----------------------------- | ------------------- |
| id            | int       | PK                            | Submission ID       |
| assignment_id | int       | FK → assignments.id, NOT NULL | Assignment          |
| student_id    | int       | FK → students.id, NOT NULL    | Student             |
| version       | int       | Default 1                     | Version number      |
| language      | varchar   | —                             | Submission language |
| status        | varchar   | —                             | Submission status   |
| score         | decimal   | Default 0                     | Final score         |
| is_late       | boolean   | Default false                 | Late flag           |
| created_at    | timestamp | Default now()                 | Timestamp           |

---

# RESULTS

**Description:** Execution results of a submission against individual test cases.

| Column        | Type      | Constraints                   | Description       |
| ------------- | --------- | ----------------------------- | ----------------- |
| id            | int       | PK                            | Result ID         |
| submission_id | int       | FK → submissions.id, NOT NULL | Submission        |
| test_case_id  | int       | FK → test_cases.id, NOT NULL  | Test case         |
| passed        | boolean   | NOT NULL                      | Test passed?      |
| stdout        | text      | —                             | Program output    |
| stderr        | text      | —                             | Error output      |
| runtime_ms    | int       | —                             | Execution time    |
| memory_kb     | int       | —                             | Memory used       |
| exit_code     | int       | —                             | Process exit code |
| created_at    | timestamp | Default now()                 | Creation time     |

---

# HINTS

**Description:** AI-generated hints for a submission.

| Column        | Type      | Constraints                   | Description            |
| ------------- | --------- | ----------------------------- | ---------------------- |
| id            | int       | PK                            | Hint ID                |
| submission_id | int       | FK → submissions.id, NOT NULL | Submission             |
| model_used    | varchar   | —                             | Model name             |
| confidence    | decimal   | 0.0–1.0                       | Model confidence score |
| hint_text     | text      | NOT NULL                      | Hint text              |
| is_helpful    | boolean   | —                             | Student feedback       |
| created_at    | timestamp | Default now()                 | Creation time          |

---

# EMBEDDINGS

**Description:** Vector embedding reference (1:1 with submission).

| Column        | Type      | Constraints                           | Description               |
| ------------- | --------- | ------------------------------------- | ------------------------- |
| id            | int       | PK                                    | Embedding ID              |
| submission_id | int       | FK → submissions.id, UNIQUE, NOT NULL | Submission                |
| vector_ref    | text      | NOT NULL                              | Pointer to vector storage |
| model_version | varchar   | —                                     | Embedding model version   |
| created_at    | timestamp | Default now()                         | Timestamp                 |

---

# SIMILARITY_FLAGS

**Description:** Plagiarism/similarity detection results for a submission.

| Column            | Type       | Constraints                           | Description              |
| ----------------- | ---------- | ------------------------------------- | ------------------------ |
| id                | int        | PK                                    | Flag ID                  |
| submission_id     | int        | FK → submissions.id, UNIQUE, NOT NULL | Submission               |
| similarity_score  | decimal    | 0.0–1.0, NOT NULL                     | Highest similarity score |
| highlighted_spans | jsonb/text | —                                     | Matched span data        |
| is_reviewed       | boolean    | Default false                         | Human-reviewed?          |
| reviewed_by       | int        | FK → users.id                         | Reviewer ID              |
| review_notes      | text       | —                                     | Notes                    |
| reviewed_at       | timestamp  | —                                     | Review time              |
| created_at        | timestamp  | Default now()                         | Creation time            |

---

# SIMILARITY_COMPARISONS

**Description:** Records which other submissions were compared during similarity check.

| Column                 | Type       | Constraints                        | Description            |
| ---------------------- | ---------- | ---------------------------------- | ---------------------- |
| similarity_id          | int        | FK → similarity_flags.id, NOT NULL | parent similarity flag |
| compared_submission_id | int        | FK → submissions.id, NOT NULL      | Compared submission    |
| match_score            | decimal    | 0.0–1.0, NOT NULL                  | Pairwise score         |
| highlighted_spans      | jsonb/text | —                                  | Match details          |

**Primary Key:** (similarity_id, compared_submission_id)

---

# PEER_REVIEWS

**Description:** Peer review records for a submission.

| Column              | Type      | Constraints                   | Description           |
| ------------------- | --------- | ----------------------------- | --------------------- |
| id                  | int       | PK                            | Peer review ID        |
| submission_id       | int       | FK → submissions.id, NOT NULL | Submission reviewed   |
| reviewer_student_id | int       | FK → students.id, NOT NULL    | Reviewer student      |
| rubric_scores       | jsonb     | NOT NULL                      | Structured rubric     |
| comments            | text      | —                             | Reviewer comments     |
| is_submitted        | boolean   | Default false                 | Submission status     |
| submitted_at        | timestamp | —                             | Final submission time |
| created_at          | timestamp | Default now()                 | Creation time         |

---

# FILES

**Description:** Files attached to submissions or uploaded by users.

| Column        | Type | Constraints         | Description |
| ------------- | ---- | ------------------- | ----------- |
| id            | int  | PK                  | File ID     |
| submission_id | int  | FK → submissions.id |             |
