#!/usr/bin/env python3
"""
Verification script for Adaptive Code Lab Refactoring.
Run this script to verify that all modules can be imported correctly 
after the Clean Architecture restructure.

Usage:
    python verify_installation.py
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print(f"Checking imports with PYTHONPATH={src_path}...\n")

def check_import(module_name, item_name=None):
    try:
        if item_name:
            exec(f"from {module_name} import {item_name}")
            print(f"✅ SUCCESS: from {module_name} import {item_name}")
        else:
            exec(f"import {module_name}")
            print(f"✅ SUCCESS: import {module_name}")
        return True
    except ImportError as e:
        print(f"❌ FAILED: {module_name} - {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {module_name} - {e}")
        return False

results = []

print("--- Core Layer (Entities) ---")
# Check all 18 entities
entities = [
    "admin", "assignment", "audit_log", "course", "embedding", 
    "enrollment", "file", "hint", "instructor", "notification", 
    "peer_review", "result", "similarity_comparison", "similarity_flag", 
    "student", "submission", "test_case", "user"
]
for entity in entities:
    # Convert implementation snake_case to ClassName logic roughly or just import module
    # We will import the module to be safe and generic
    results.append(check_import(f"core.entities.{entity}"))

print("\n--- Core Layer (Services) ---")
services = [
    "auth_service", "embedding_service", "instructor_service", 
    "similarity_flag_service", "similarity_service", "student_service"
]
for service in services:
    results.append(check_import(f"core.services.{service}"))

print("\n--- Core Layer (Exceptions) ---")
results.append(check_import("core.exceptions.auth_error", "AuthError"))
results.append(check_import("core.exceptions.validation_error", "ValidationError"))

print("\n--- Infrastructure Layer (Repositories) ---")
repositories = [
    "admin_repository", "assignment_repository", "audit_log_repository",
    "course_repository", "database", "embedding_repository",
    "enrollment_repository", "file_repository", "flag_repository",
    "hint_repository", "instructor_repository", "notification_repository",
    "peer_review_repository", "result_repository", "similarity_comparison_repository",
    "similarity_flag_repository", "student_repository", "submission_repository",
    "test_case_repository", "user_repository"
]
for repo in repositories:
    results.append(check_import(f"infrastructure.repositories.{repo}"))

print("\n--- Infrastructure Layer (AI) ---")
results.append(check_import("infrastructure.ai.gemini_client", "GeminiClient"))

print("\n--- Infrastructure Layer (Database) ---")
results.append(check_import("infrastructure.database.connection", "DatabaseManager"))
results.append(check_import("infrastructure.database.create_db", "create_database"))

print("\n--- Web Layer ---")
results.append(check_import("web.app", "create_app"))

print("\n" + "="*40)
if all(results):
    print("ALL CHECKS PASSED! The refactoring is verified.")
    sys.exit(0)
else:
    print(f"SOME CHECKS FAILED. ({results.count(False)} failures)")
    sys.exit(1)
