import pytest
from unittest.mock import Mock
from core.services.result_service import ResultService


@pytest.fixture
def mock_result_repo():
    return Mock()


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def mock_testcase_repo():
    return Mock()


@pytest.fixture
def result_service(mock_result_repo, mock_submission_repo, mock_testcase_repo):
    return ResultService(mock_result_repo, mock_submission_repo, mock_testcase_repo)


class TestResultService:
    """Test suite for ResultService"""

    def test_save_testcase_result(self, result_service, mock_result_repo):
        """Test saving a test case result"""
        mock_result_repo.save_result.return_value = Mock()

        result = result_service.save_testcase_result(
            submission_id=1,
            test_case_id=1,
            passed=True,
            stdout="output",
            stderr="",
            runtime_ms=100,
            memory_kb=1024,
            exit_code=0
        )

        mock_result_repo.save_result.assert_called_once()
        args, _ = mock_result_repo.save_result.call_args
        res = args[0]
        assert res.passed is True
        assert res.stdout == "output"

    def test_save_testcase_result_with_error(self, result_service, mock_result_repo):
        """Test saving a failed test case result"""
        mock_result_repo.save_result.return_value = Mock()

        result = result_service.save_testcase_result(
            submission_id=1,
            test_case_id=1,
            passed=False,
            stdout="",
            stderr="Error occurred",
            runtime_ms=50,
            memory_kb=512,
            exit_code=1,
            error_message="Runtime error"
        )

        args, _ = mock_result_repo.save_result.call_args
        res = args[0]
        assert res.passed is False
        assert res.error_message == "Runtime error"

    def test_list_results_for_submission(self, result_service, mock_result_repo):
        """Test listing results for submission"""
        results = [Mock(), Mock()]
        mock_result_repo.find_by_submission.return_value = results

        result = result_service.list_results_for_submission(1)

        mock_result_repo.find_by_submission.assert_called_once_with(1)
        assert result == results

    def test_calculate_submission_score(self, result_service, mock_result_repo,
                                         mock_submission_repo, mock_testcase_repo):
        """Test calculating submission score"""
        # Setup results
        result1 = Mock()
        result1.issuccessful.return_value = True
        result1.get_test_case_id.return_value = 1

        result2 = Mock()
        result2.issuccessful.return_value = True
        result2.get_test_case_id.return_value = 2

        mock_result_repo.find_by_submission.return_value = [result1, result2]

        # Setup testcases
        tc1 = Mock()
        tc1.get_id.return_value = 1
        tc1.points = 10

        tc2 = Mock()
        tc2.get_id.return_value = 2
        tc2.points = 20

        mock_testcase_repo.list_by_assignment.return_value = [tc1, tc2]

        # Setup submission
        submission = Mock()
        submission.get_assignment_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        mock_submission_repo.update.return_value = submission

        result_service.calculate_submission_score(1)

        assert submission.score == 30
        assert submission.status == "graded"
        mock_submission_repo.update.assert_called_once()

    def test_calculate_submission_score_partial(self, result_service, mock_result_repo,
                                                  mock_submission_repo, mock_testcase_repo):
        """Test calculating partial score when some tests fail"""
        # Setup results - one passes, one fails
        result1 = Mock()
        result1.issuccessful.return_value = True
        result1.get_test_case_id.return_value = 1

        result2 = Mock()
        result2.issuccessful.return_value = False  # Failed
        result2.get_test_case_id.return_value = 2

        mock_result_repo.find_by_submission.return_value = [result1, result2]

        # Setup testcases
        tc1 = Mock()
        tc1.get_id.return_value = 1
        tc1.points = 10

        tc2 = Mock()
        tc2.get_id.return_value = 2
        tc2.points = 20

        mock_testcase_repo.list_by_assignment.return_value = [tc1, tc2]

        # Setup submission
        submission = Mock()
        submission.get_assignment_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        mock_submission_repo.update.return_value = submission

        result_service.calculate_submission_score(1)

        assert submission.score == 10  # Only first test passed
