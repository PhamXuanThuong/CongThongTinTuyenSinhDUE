from django.core.management.base import BaseCommand
from admissions import knowledge_sync


class Command(BaseCommand):
    help = "Đồng bộ dữ liệu website (ngành, điểm chuẩn, học phí, FAQ, tin tức...) vào kho kiến thức Chatbot"

    def handle(self, *args, **options):
        stats = knowledge_sync.sync()
        self.stdout.write(self.style.SUCCESS(
            f"Xong: {stats['tong']} đoạn kiến thức, thêm mới {stats['them_moi']}, xóa {stats['xoa']}"))
