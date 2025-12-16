from datetime import datetime
from core.entities.hint import Hint

class HintService:
    def __init__(self, hint_repo, submission_repo, ai_client):
        self.hint_repo = hint_repo
        self.submission_repo = submission_repo
        self.ai_client = ai_client

    def generate_hint(self, submission_id):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise Exception("Submission not found")

        # Example AI call
        ai_response = self.ai_client.generate_hint(
            submission_id=submission_id
        )

        hint = Hint(
            id=None,
            submission_id=submission_id,
            model_used=ai_response["model"],
            confidence=ai_response["confidence"],
            hint_text=ai_response["text"],
            is_helpful=False,
            feedback=None,
            created_at=datetime.utcnow()
        )

        return self.hint_repo.create(hint)

    def mark_hint_helpful(self, hint_id):
        hint = self.hint_repo.get_by_id(hint_id)
        if not hint:
            raise Exception("Hint not found")

        hint.mark_helpful()
        return self.hint_repo.update(hint)

    def mark_hint_not_helpful(self, hint_id):
        hint = self.hint_repo.get_by_id(hint_id)
        if not hint:
            raise Exception("Hint not found")

        hint.mark_not_helpful()
        return self.hint_repo.update(hint)

    def list_hints_for_submission(self, submission_id):
        return self.hint_repo.list_by_submission(submission_id)
