import os
import tempfile
from infrastructure.database import migrations

def test_run_migrations_creates_all_tables():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp_db:
        db_path = tmp_db.name
        tables_dir = os.path.join(os.path.dirname(__file__), "../../src/infrastructure/database/schema")

        tables = migrations.run_migrations(db_path=db_path, tables_dir=tables_dir)

        # Basic checks
        assert "users" in tables
        assert "admins" in tables
        assert "assignments" in tables