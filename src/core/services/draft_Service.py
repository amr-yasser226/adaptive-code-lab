from core.entities.draft import Draft
from datetime import datetime

class DraftService:
    def __init__(self, draft_repo):
        self.draft_repo = draft_repo

    def get_latest_draft(self, user_id: int, assignment_id: int):
        return self.draft_repo.get_latest(user_id, assignment_id)

    def save_draft(self, user_id: int, assignment_id: int, content: str, metadata: str = None):
        # Determine new version number
        last = self.draft_repo.get_latest(user_id, assignment_id)
        new_version = (last.version + 1) if last and getattr(last, 'version', None) else 1

        draft = Draft(
            id=None,
            user_id=user_id,
            assignment_id=assignment_id,
            content=content,
            metadata=metadata,
            version=new_version,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return self.draft_repo.create(draft)
