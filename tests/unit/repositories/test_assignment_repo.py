import pytest
from core.entities.assignment import Assignment


@pytest.mark.repo
@pytest.mark.unit
class TestAssignmentRepo:
    """Test suite for Assignments_repo"""
    
    def test_create_assignment(self, sample_course, assignment_repo):
        """Test creating a new assignment"""
        assignment = Assignment(
            id=None,
            course_id=sample_course.get_id(),
            title="Lab 2",
            description="Implement sorting algorithms",
            release_date="2024-02-01",
            due_date="2024-02-14",
            max_points=50,
            is_published=False,
            allow_late_submissions=False,
            late_submission_penalty=0.0,
            created_at=None,
            updated_at=None
        )
        
        saved = assignment_repo.create(assignment)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.title == "Lab 2"
    
    def test_get_by_id_returns_assignment(self, sample_assignment, assignment_repo):
        """Test retrieving assignment by ID"""
        retrieved = assignment_repo.get_by_id(sample_assignment.get_id())
        
        assert retrieved is not None
        assert retrieved.title == sample_assignment.title

    def test_get_by_id_not_found(self, assignment_repo):
        """Line 22: get_by_id returns None for non-existent ID"""
        assert assignment_repo.get_by_id(9999) is None
    
    def test_update_assignment(self, sample_assignment, assignment_repo):
        """Test updating assignment"""
        sample_assignment.title = "Updated Assignment"
        sample_assignment.max_points = 150
        
        updated = assignment_repo.update(sample_assignment)
        
        assert updated.title == "Updated Assignment"
        assert updated.max_points == 150
    
    def test_publish_assignment(self, sample_assignment, assignment_repo):
        """Test publishing an assignment"""
        published = assignment_repo.publish(sample_assignment.get_id())
        
        assert published.is_published is True
    
    def test_unpublish_assignment(self, sample_assignment, assignment_repo):
        """Test unpublishing an assignment"""
        unpublished = assignment_repo.unpublish(sample_assignment.get_id())
        
        assert unpublished.is_published is False
    
    def test_extend_deadline(self, sample_assignment, assignment_repo):
        """Test extending deadline"""
        new_date = "2024-01-30"
        extended = assignment_repo.extend_deadline(
            sample_assignment.get_id(),
            new_date
        )
        
        assert extended.due_date == new_date
    
    def test_list_by_course(self, sample_course, assignment_repo):
        """Test listing assignments by course"""
        # Create multiple assignments
        for i in range(3):
            assignment = Assignment(
                id=None,
                course_id=sample_course.get_id(),
                title=f"Assignment {i}",
                description="Description",
                release_date="2024-01-01",
                due_date="2024-01-15",
                max_points=100,
                is_published=True,
                allow_late_submissions=True,
                late_submission_penalty=0.1,
                created_at=None,
                updated_at=None
            )
            assignment_repo.create(assignment)
        
        assignments = assignment_repo.list_by_course(sample_course.get_id())
        
        assert len(assignments) >= 3

    def test_get_all(self, assignment_repo, sample_assignment):
        """Test getting all assignments"""
        all_assignments = assignment_repo.get_all()
        assert len(all_assignments) >= 1
        assert any(a.get_id() == sample_assignment.get_id() for a in all_assignments)

    def test_create_error(self, assignment_repo, sample_course):
        """Line 68-71: create handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        assignment_repo.db = mock_db
        
        assignment = Assignment(
            id=None,
            course_id=sample_course.get_id(),
            title="T",
            description="D",
            release_date="2024-01-01",
            due_date="2024-01-30",
            max_points=100,
            is_published=True,
            allow_late_submissions=True,
            late_submission_penalty=0.1,
            created_at=None,
            updated_at=None
        )
        assert assignment_repo.create(assignment) is None
        mock_db.rollback.assert_called_once()

    def test_update_error(self, assignment_repo, sample_assignment):
        """Line 102-105: update handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        assignment_repo.db = mock_db
        
        assert assignment_repo.update(sample_assignment) is None
        mock_db.rollback.assert_called_once()

    def test_publish_error(self, assignment_repo):
        """Line 117-120: publish handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        assignment_repo.db = mock_db
        
        assert assignment_repo.publish(1) is None
        mock_db.rollback.assert_called_once()

    def test_unpublish_error(self, assignment_repo):
        """Line 132-135: unpublish handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        assignment_repo.db = mock_db
        
        assert assignment_repo.unpublish(1) is None
        mock_db.rollback.assert_called_once()

    def test_extend_deadline_error(self, assignment_repo):
        """Line 147-150: extend_deadline handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        assignment_repo.db = mock_db
        
        assert assignment_repo.extend_deadline(1, "2024") is None
        mock_db.rollback.assert_called_once()
