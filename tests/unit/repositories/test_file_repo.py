import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.file import File


@pytest.mark.repo
@pytest.mark.unit
class TestFileRepo:
    """Test suite for FileRepository"""
    
    def test_save_file(self, sample_submission, sample_student, file_repo):
        """Test saving a new file"""
        file = File(
            id=None,
            submission_id=sample_submission.get_id(),
            uploader_id=sample_student.get_id(),
            path="/submissions/1/",
            file_name="solution.py",
            content_type="text/x-python",
            size_bytes=1024,
            check_sum="abc123def456",
            storage_url="/storage/solution.py",
            created_at=None
        )
        
        saved = file_repo.save_file(file)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.file_name == "solution.py"
    
    def test_get_by_id_returns_file(self, sample_submission, sample_student, file_repo):
        """Test retrieving file by ID"""
        file = File(
            id=None,
            submission_id=sample_submission.get_id(),
            uploader_id=sample_student.get_id(),
            path="/submissions/1/",
            file_name="test.txt",
            content_type="text/plain",
            size_bytes=512,
            check_sum="xyz789",
            storage_url="/storage/test.txt",
            created_at=None
        )
        saved = file_repo.save_file(file)
        
        retrieved = file_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.file_name == "test.txt"

    def test_get_by_id_not_found(self, file_repo):
        """Line 19: get_by_id returns None for non-existent ID"""
        assert file_repo.get_by_id(9999) is None
    
    def test_delete_file(self, sample_submission, sample_student, file_repo):
        """Test deleting file"""
        file = File(
            id=None,
            submission_id=sample_submission.get_id(),
            uploader_id=sample_student.get_id(),
            path="/submissions/1/",
            file_name="delete_me.py",
            content_type="text/x-python",
            size_bytes=256,
            check_sum="delete123",
            storage_url="/storage/delete_me.py",
            created_at=None
        )
        saved = file_repo.save_file(file)
        
        file_repo.delete(saved.get_id())
        retrieved = file_repo.get_by_id(saved.get_id())
        
        assert retrieved is None

    def test_save_error(self, file_repo, sample_submission, sample_student):
        """Line 61-64: save_file handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        file_repo.db = mock_db
        file = File(None, sample_submission.get_id(), sample_student.get_id(), "p", "f", "t", 0, "c", "s", None)
        assert file_repo.save_file(file) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, file_repo):
        """Line 71-73: delete handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        file_repo.db = mock_db
        with pytest.raises(sqlite3.Error):
            file_repo.delete(1)
        mock_db.rollback.assert_called_once()
    
    def test_find_by_submission(self, sample_submission, sample_student, file_repo):
        """Test finding files by submission"""
        for i in range(3):
            file = File(
                id=None,
                submission_id=sample_submission.get_id(),
                uploader_id=sample_student.get_id(),
                path="/submissions/1/",
                file_name=f"file{i}.py",
                content_type="text/x-python",
                size_bytes=100 * (i+1),
                check_sum=f"checksum{i}",
                storage_url=f"/storage/file{i}.py",
                created_at=None
            )
            file_repo.save_file(file)
        
        files = file_repo.find_by_submission(sample_submission.get_id())
        assert len(files) >= 3