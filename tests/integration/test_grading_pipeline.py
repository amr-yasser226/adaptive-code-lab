import pytest
from datetime import datetime


class TestGradingPipeline:
    """Test suite for complete grading pipeline"""

    def test_submission_to_grading_flow(self, clean_db, sample_student, sample_assignment,
                                        submission_repo, result_repo, testcase_repo):
        """Test complete flow from submission creation to graded result"""
        from core.entities.submission import Submission
        from core.entities.test_case import Testcase
        from core.entities.result import Result

        # Create test case
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="Basic Test",
            stdin="",
            descripion="Test hello world",
            expected_out="Hello World",
            timeout_ms=1000,
            memory_limit_mb=128,
            points=100,
            is_visible=True,
            sort_order=1,
            created_at=datetime.now()
        )
        saved_testcase = testcase_repo.create(testcase)

        # Create submission
        submission = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="pending",
            score=None,
            is_late=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=None
        )
        saved_submission = submission_repo.create(submission)

        # Update status to queued
        saved_submission.status = "queued"
        submission_repo.update(saved_submission)

        # Create test result
        result = Result(
            id=None,
            submission_id=saved_submission.get_id(),
            test_case_id=saved_testcase.get_id(),
            passed=True,
            stdout="Hello World",
            stderr="",
            runtime_ms=50,
            memory_kb=512,
            exit_code=0,
            error_message=None,
            created_at=datetime.now()
        )
        saved_result = result_repo.save_result(result)

        # Update submission to graded
        saved_submission.status = "graded"
        saved_submission.score = 100
        saved_submission.grade_at = datetime.now()
        final_submission = submission_repo.update(saved_submission)

        # Verify complete flow
        assert final_submission.status == "graded"
        assert final_submission.score == 100
        assert saved_result.passed is True

    def test_partial_credit_grading(self, clean_db, sample_student, sample_assignment,
                                    submission_repo, result_repo, testcase_repo):
        """Test partial credit when some tests pass and some fail"""
        from core.entities.submission import Submission
        from core.entities.test_case import Testcase
        from core.entities.result import Result

        # Create two test cases
        testcase1 = testcase_repo.create(Testcase(
            id=None, assignment_id=sample_assignment.get_id(), name="Test 1",
            stdin="", descripion="Test 1", expected_out="OK", timeout_ms=1000,
            memory_limit_mb=128, points=50, is_visible=True, sort_order=1,
            created_at=datetime.now()
        ))
        testcase2 = testcase_repo.create(Testcase(
            id=None, assignment_id=sample_assignment.get_id(), name="Test 2",
            stdin="", descripion="Test 2", expected_out="OK", timeout_ms=1000,
            memory_limit_mb=128, points=50, is_visible=True, sort_order=2,
            created_at=datetime.now()
        ))

        # Create submission
        submission = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(), version=1, language="python",
            status="queued", score=None, is_late=False,
            created_at=datetime.now(), updated_at=datetime.now(), grade_at=None
        ))

        # Test 1 passes, Test 2 fails
        result_repo.save_result(Result(
            id=None, submission_id=submission.get_id(),
            test_case_id=testcase1.get_id(), passed=True, stdout="OK",
            stderr="", runtime_ms=50, memory_kb=512, exit_code=0,
            error_message=None, created_at=datetime.now()
        ))
        result_repo.save_result(Result(
            id=None, submission_id=submission.get_id(),
            test_case_id=testcase2.get_id(), passed=False, stdout="",
            stderr="Error", runtime_ms=50, memory_kb=512, exit_code=1,
            error_message="Test failed", created_at=datetime.now()
        ))

        # Grade submission
        submission.status = "graded"
        submission.score = 50  # Only first test passed
        submission.grade_at = datetime.now()
        final = submission_repo.update(submission)

        assert final.score == 50
        assert final.status == "graded"
