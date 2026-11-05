from django.apps import AppConfig


class AdmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admissions'
    verbose_name = 'Admissions & Academic Advisory'

    def ready(self):
        # Sửa dữ liệu trong admin -> Chatbot tự cập nhật kiến thức
        from . import knowledge_sync
        knowledge_sync.connect_signals()
