from django.core.management.base import BaseCommand
from admissions import knowledge_sync


class Command(BaseCommand):
    help = "Đồng bộ tổng hợp chung dữ liệu website (ngành, khoa, điểm chuẩn, học phí, FAQ, tin tức...) vào kho kiến thức Chatbot"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Xóa toàn bộ các đoạn kiến thức website cũ trước khi nạp lại',
        )

    def handle(self, *args, **options):
        clear_all = options.get('clear', False)

        def report(msg):
            self.stdout.write(self.style.NOTICE(f"[Sync] {msg}"))

        self.stdout.write(self.style.MIGRATE_HEADING("Bắt đầu đồng bộ tổng hợp kho kiến thức Chatbot..."))
        stats = knowledge_sync.sync(
            clear_all=clear_all,
            progress_callback=report
        )
        self.stdout.write(self.style.SUCCESS(
            f"Hoàn thành: Tổng {stats['tong']} đoạn, thêm mới {stats['them_moi']}, xóa {stats['xoa']} đoạn cũ."
        ))
