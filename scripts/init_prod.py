import os
import shutil
import sys
import subprocess
from pathlib import Path

def main():
    # Navigate to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("==========================================")
    print("ACCL PRODUCTION INITIALIZATION")
    print("==========================================")

    # 1. Clean up existing database
    db_path = project_root / 'data' / 'Accl_DB.db'
    print(f"[1/3] Cleaning up old database at {db_path}...")
    if db_path.exists():
        try:
            db_path.unlink()
            print("    ✓ Removed existing database.")
        except Exception as e:
            print(f"    ⚠ Could not remove database: {e}")
    else:
        print("    - No existing database found.")

    # Find the correct python executable
    python_exec = sys.executable

    # 2. Run migrations
    print("[2/3] Running migrations (Schema creation)...")
    env = os.environ.copy()
    src_path = str(project_root / 'src')
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = src_path

    try:
        subprocess.run([python_exec, "src/infrastructure/database/migrations.py"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running migrations: {e}")
        sys.exit(1)

    # 3. Seed full demo data
    print("[3/3] Seeding full demo data (All 16 FRs)...")
    try:
        subprocess.run([python_exec, "scripts/full_demo_seed.py"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error seeding data: {e}")
        sys.exit(1)

    print("")
    print("==========================================")
    print("SUCCESS: Fresh production database ready!")
    print(f"To start the server, run: {python_exec} scripts/run_prod.py")
    print("==========================================")

if __name__ == "__main__":
    main()
