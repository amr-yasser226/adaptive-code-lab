from core.entities.draft import Draft
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DraftService:
    def __init__(self, draft_repo):
        self.draft_repo = draft_repo

    def get_latest_draft(self, user_id: int, assignment_id: int):
        return self.draft_repo.get_latest(user_id, assignment_id)

    def save_draft(self, user_id: int, assignment_id: int, content: str, language: str = 'python'):
        try:
            draft = Draft(
                id=None,
                user_id=user_id,
                assignment_id=assignment_id,
                content=content,
                language=language
            )

            saved = self.draft_repo.create(draft)
            if not saved:
                logger.warning('Failed to persist draft for user=%s assignment=%s', user_id, assignment_id)
            return saved
        except Exception as e:
            logger.exception('Error saving draft: %s', e)
            raise
