from sqlalchemy.exc import SQLAlchemyError
from Model.Testcase_model import Testcase

class Testcase_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                id, assignment_id, name, stdin, descripion,
                expected_out, timeout_ms, memory_limit_mb,
                points, is_visible, sort_order, created_at
            FROM test_cases
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Testcase(
            id=row.id,
            assignment_id=row.assignment_id,
            name=row.name,
            stdin=row.stdin,
            descripion=row.descripion,
            expected_out=row.expected_out,
            timeout_ms=row.timeout_ms,
            memory_limit_mb=row.memory_limit_mb,
            points=row.points,
            is_visible=row.is_visible,
            sort_order=row.sort_order,
            created_at=row.created_at
        )

    def create(self, testcase: Testcase):
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO test_cases (
                    assignment_id, name, stdin, descripion,
                    expected_out, timeout_ms, memory_limit_mb,
                    points, is_visible, sort_order, created_at
                )
                VALUES (
                    :assignment_id, :name, :stdin, :descripion,
                    :expected_out, :timeout_ms, :memory_limit_mb,
                    :points, :is_visible, :sort_order, :created_at
                )
            """
            self.db.execute(query, {
                "assignment_id": testcase.get_assignment_id(),
                "name": testcase.name,
                "stdin": testcase.stdin,
                "descripion": testcase.descripion,
                "expected_out": testcase.expected_out,
                "timeout_ms": testcase.timeout_ms,
                "memory_limit_mb": testcase.memory_limit_mb,
                "points": testcase.points,
                "is_visible": int(testcase.is_visible),
                "sort_order": testcase.sort_order,
                "created_at": testcase.created_at
            })
            new_id = self.db.execute("SELECT last_insert_rowid() AS id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def update(self, testcase: Testcase):
        try:
            self.db.begin_transaction()
            query = """
                UPDATE test_cases
                SET 
                    name = :name,
                    stdin = :stdin,
                    descripion = :descripion,
                    expected_out = :expected_out,
                    timeout_ms = :timeout_ms,
                    memory_limit_mb = :memory_limit_mb,
                    points = :points,
                    is_visible = :is_visible,
                    sort_order = :sort_order
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": testcase.get_id(),
                "name": testcase.name,
                "stdin": testcase.stdin,
                "descripion": testcase.descripion,
                "expected_out": testcase.expected_out,
                "timeout_ms": testcase.timeout_ms,
                "memory_limit_mb": testcase.memory_limit_mb,
                "points": testcase.points,
                "is_visible": int(testcase.is_visible),
                "sort_order": testcase.sort_order
            })
            self.db.commit()
            return self.get_by_id(testcase.get_id())
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def delete(self, id: int):
        try:
            self.db.begin_transaction()
            self.db.execute("DELETE FROM test_cases WHERE id = :id", {"id": id})
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def list_by_assignment(self, assignment_id: int):
        query = """
            SELECT *
            FROM test_cases
            WHERE assignment_id = :aid
            ORDER BY sort_order ASC
        """
        result = self.db.execute(query, {"aid": assignment_id})
        rows = result.fetchall()
        return [
            Testcase(
                id=row.id,
                assignment_id=row.assignment_id,
                name=row.name,
                stdin=row.stdin,
                descripion=row.descripion,
                expected_out=row.expected_out,
                timeout_ms=row.timeout_ms,
                memory_limit_mb=row.memory_limit_mb,
                points=row.points,
                is_visible=row.is_visible,
                sort_order=row.sort_order,
                created_at=row.created_at
            )
            for row in rows
        ]
