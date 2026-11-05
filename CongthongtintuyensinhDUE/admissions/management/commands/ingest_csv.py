from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from tuyensinh import rag


class Command(BaseCommand):
    help = "Nạp các file CSV kiến thức (data/, document/) vào vector store"

    def handle(self, *args, **kwargs):
        for folder in ("data", "document"):
            for p in (Path(settings.BASE_DIR) / folder).glob("*.csv"):
                n = rag.index_csv_rows(p)
                self.stdout.write(self.style.SUCCESS(f"{p.name}: {n} dòng"))
