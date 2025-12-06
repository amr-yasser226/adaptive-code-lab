import pytest
import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Print for debugging
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Verify DB path is set
db_path = os.getenv("ACCL_DB_PATH")
if db_path:
    print(f"Using DB: {project_root / db_path}")
else:
    print("WARNING: ACCL_DB_PATH not set in .env")


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory path"""
    return project_root


@pytest.fixture(scope="session")
def src_path_fixture():
    """Return the src directory path"""
    return src_path