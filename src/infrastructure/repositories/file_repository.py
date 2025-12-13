from sqlalchemy.exc import SQLAlchemyError
from core.entities.file import File

class File_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT
                f.id, f.submission_id, f.uploader_id, f.path, f.filename,
                f.content_type, f.size_bytes, f.checksum, f.storage_url, f.created_at
            FROM files f
            WHERE f.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return File(
            id=row.id,
            submission_id=row.submission_id,
            uploader_id=row.uploader_id,
            path=row.path,
            file_name=row.filename,
            content_type=row.content_type,
            size_bytes=row.size_bytes,
            check_sum=row.checksum,  # Changed from checksum to check_sum
            storage_url=row.storage_url,
            created_at=row.created_at
        )

    def save_file(self, file: File):
        """
        FIXED: getById() -> get_by_id()
        """
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO files (
                    submission_id, path, filename, content_type,
                    size_bytes, uploader_id, checksum, storage_url
                )
                VALUES (
                    :submission_id, :path, :filename, :content_type,
                    :size_bytes, :uploader_id, :checksum, :storage_url
                )
            """
            self.db.execute(query, {
                "submission_id": file.get_submission_id(),
                "path": file.path,
                "filename": file.file_name,
                "content_type": file.content_type,
                "size_bytes": file.size_bytes,
                "uploader_id": file.uploader_id,
                "checksum": file.checksum,
                "storage_url": file.storage_url
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)  # FIXED: was getById(new_id)
        except Exception as e:
            self.db.rollback()
            print("Error saving file:", e)
            return None

    def delete(self, id: int):
        try:
            self.db.begin_transaction()
            query = "DELETE FROM files WHERE id = :id"
            self.db.execute(query, {"id": id})
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def find_by_submission(self, submissionId: int):
        query = """
            SELECT
                f.id, f.submission_id, f.uploader_id, f.path, f.filename,
                f.content_type, f.size_bytes, f.checksum, f.storage_url, f.created_at
            FROM files f
            WHERE f.submission_id = :submission_id
            ORDER BY f.created_at DESC
        """
        result = self.db.execute(query, {"submission_id": submissionId})
        files = []
        for row in result.fetchall():
            files.append(File(
                id=row.id,
                submission_id=row.submission_id,
                uploader_id=row.uploader_id,
                path=row.path,
                file_name=row.filename,
                content_type=row.content_type,
                size_bytes=row.size_bytes,
                check_sum=row.checksum, # Changed from checksum to check_sum
                storage_url=row.storage_url,
                created_at=row.created_at
            ))
        return files