import pytest
from datetime import datetime
from core.entities.file import File


class TestFile:
    """Test suite for File entity"""

    def test_init(self):
        """Test File initialization"""
        now = datetime.now()
        file = File(
            id=1,
            submission_id=10,
            uploader_id=5,
            path="/submissions/10/",
            file_name="solution.py",
            content_type="text/x-python",
            size_bytes=1024,
            check_sum="abc123",
            storage_url="/storage/solution.py",
            created_at=now
        )

        assert file.get_id() == 1
        assert file.get_submission_id() == 10
        assert file.uploader_id == 5
        assert file.file_name == "solution.py"
        assert file.size_bytes == 1024

    def test_get_id(self):
        """Test get_id getter"""
        file = File(
            id=42, submission_id=1, uploader_id=1, path="/",
            file_name="test.py", content_type="text/plain",
            size_bytes=100, check_sum="x", storage_url="/",
            created_at=datetime.now()
        )
        assert file.get_id() == 42

    def test_get_submission_id(self):
        """Test get_submission_id getter"""
        file = File(
            id=1, submission_id=99, uploader_id=1, path="/",
            file_name="test.py", content_type="text/plain",
            size_bytes=100, check_sum="x", storage_url="/",
            created_at=datetime.now()
        )
        assert file.get_submission_id() == 99

    def test_public_attributes(self):
        """Test public attributes are accessible"""
        now = datetime.now()
        file = File(
            id=1, submission_id=1, uploader_id=5, path="/path/",
            file_name="main.cpp", content_type="text/x-c++",
            size_bytes=2048, check_sum="hash123", storage_url="/store/",
            created_at=now
        )

        assert file.uploader_id == 5
        assert file.path == "/path/"
        assert file.file_name == "main.cpp"
        assert file.content_type == "text/x-c++"
        assert file.size_bytes == 2048
        assert file.checksum == "hash123"
        assert file.storage_url == "/store/"
        assert file.created_at == now
