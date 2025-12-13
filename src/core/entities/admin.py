from core.entities.user import User
class Admin(User):
    def __init__(self, id, name, email, password, created_at, updated_at, is_active=True,privileges=None):
        super().__init__(id=id, name=name, email=email, password=password, role="admin", created_at=created_at, updated_at=updated_at, is_active=is_active)
        self.privileges = privileges
    
    # def manage_user_accounts(self, user_id, action):
    #     pass
    # def generate_reports(self, report_type):
    #     pass
    # def configure_system_settings(self, setting, value):
    #     pass
    # def export_db_dump(self, file_path):
    #     pass
    