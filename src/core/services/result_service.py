from datetime import datetime
from core.entities.result import Result
class ResultService:
    def __init__(self, result_repo, submission_repo, testcase_repo):
        self.result_repo = result_repo
        self.submission_repo = submission_repo
        self.testcase_repo = testcase_repo

    def save_testcase_result(
        self,
        submission_id,
        test_case_id,
        passed,
        stdout,
        stderr,
        runtime_ms,
        memory_kb,
        exit_code,
        error_message=None
    ):
        result = Result(
            id=None,
            submission_id=submission_id,
            test_case_id=test_case_id,
            passed=passed,
            stdout=stdout,
            stderr=stderr,
            runtime_ms=runtime_ms,
            memory_kb=memory_kb,
            exit_code=exit_code,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        return self.result_repo.save_result(result)

    def list_results_for_submission(self, submission_id):
        return self.result_repo.find_by_submission(submission_id)

    def calculate_submission_score(self, submission_id):
        results = self.result_repo.find_by_submission(submission_id)
        testcases = self.testcase_repo.list_by_assignment(
            self.submission_repo.get_by_id(submission_id).get_assignment_id()
        )

        score = 0
        for r in results:
            if r.issuccessful():
                tc = next(tc for tc in testcases if tc.get_id() == r.get_test_case_id())
                score += tc.points

        submission = self.submission_repo.get_by_id(submission_id)
        submission.score = score
        submission.status = "graded"
        submission.grade_at = datetime.utcnow()

        return self.submission_repo.update(submission)
