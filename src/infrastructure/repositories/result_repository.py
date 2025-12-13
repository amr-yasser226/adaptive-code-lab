from sqlalchemy.exc import SQLAlchemyError
from Backend.Model.Results_model import Result


class Result_repo:
    def __init__(self, db):
        self.db = db


    def get_by_id(self, id: int):
        query = """
            SELECT 
                r.id, r.submission_id, r.test_case_id, r.passed, r.stdout,
                r.stderr, r.runtime_ms, r.memory_kb, r.exit_code, r.error_message, r.created_at
            FROM results r
            WHERE r.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Result(
            id=row.id,
            submission_id=row.submission_id,
            test_case_id=row.test_case_id,
            passed=row.passed,
            stdout=row.stdout,
            stderr=row.stderr,
            runtime_ms=row.runtime_ms,
            memory_kb=row.memory_kb,
            exit_code=row.exit_code,
            error_message=row.error_message,
            created_at=row.created_at
        )
    
    def save_result(self, result: Result):
        try:
            self.db.begin_transaction()

            query = """
                INSERT INTO results (
                    submission_id, test_case_id, passed, stdout,
                    stderr, runtime_ms, memory_kb, exit_code, error_message
                )
                VALUES (
                    :submission_id, :test_case_id, :passed, :stdout,
                    :stderr, :runtime_ms, :memory_kb, :exit_code, :error_message
                )
            """
            self.db.execute(query, {
                "submission_id": result.get_submission_id(),
                "test_case_id": result.get_test_case_id(),
                "passed": int(result.passed),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "runtime_ms": result.runtime_ms,
                "memory_kb": result.memory_kb,
                "exit_code": result.exit_code,
                "error_message": result.error_message
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)
        except Exception as e : 
            self.db.rollback()
            print("Error saving result:", e)
            return None

    def find_by_submission(self, submissionId: int):
        query = """
            SELECT 
                r.id, r.submission_id, r.test_case_id, r.passed, r.stdout,
                r.stderr, r.runtime_ms, r.memory_kb, r.exit_code, r.error_message, r.created_at
            FROM results r
            WHERE r.submission_id = :submission_id
        """
        result = self.db.execute(query, {"submission_id": submissionId})
        results = []
        for row in result.fetchall():
            results.append(Result(
                id=row.id,
                submission_id=row.submission_id,
                test_case_id=row.test_case_id,
                passed=row.passed,
                stdout=row.stdout,
                stderr=row.stderr,
                runtime_ms=row.runtime_ms,
                memory_kb=row.memory_kb,
                exit_code=row.exit_code,
                error_message=row.error_message,
                created_at=row.created_at
            ))
        return results
