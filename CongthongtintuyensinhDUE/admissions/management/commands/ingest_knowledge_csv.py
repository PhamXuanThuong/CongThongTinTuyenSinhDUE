"""Nạp file kiến thức CSV (định dạng due_knowledge_base_merged.csv) vào kho Chatbot.

    python manage.py nap_kien_thuc_csv data/due_knowledge_base_merged.csv

Mỗi dòng = 1 chủ đề; nội dung dài được cắt thành nhiều đoạn, mỗi đoạn đều kèm tên chủ đề
để AI tìm đúng. Chạy lại lệnh sẽ thay toàn bộ dữ liệu cũ của cùng file.
"""
import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from admissions.models import DocumentChunk
from admissions.rag import chunk_text, embed_texts


class Command(BaseCommand):
    help = "Nạp file CSV kiến thức tuyển sinh vào kho kiến thức Chatbot"

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, **options):
        source = f"Tài liệu tuyển sinh: {Path(path).name}"
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))

        texts = []
        for r in rows:
            head = f"Chủ đề: {(r.get('chu_de') or '').strip()}"
            if (r.get('cau_hoi_mau') or '').strip():
                head += f"\nCâu hỏi thường gặp: {r['cau_hoi_mau'].strip()}"
            tail = f"\nLiên hệ/nguồn: {r['lien_he_nguon'].strip()}" if (r.get('lien_he_nguon') or '').strip() else ""
            for piece in chunk_text(r.get("noi_dung") or "", size=1500, overlap=200):
                texts.append(f"{head}\nNội dung: {piece}{tail}")

        self.stdout.write(f"{len(rows)} dòng -> {len(texts)} đoạn, đang tạo embedding...")
        vectors = embed_texts(texts)
        DocumentChunk.objects.filter(document__isnull=True, source=source).delete()
        DocumentChunk.objects.bulk_create([
            DocumentChunk(document=None, source=source, chunk_index=i, content=t, embedding=v)
            for i, (t, v) in enumerate(zip(texts, vectors))
        ])
        self.stdout.write(self.style.SUCCESS(f"Đã nạp {len(texts)} đoạn từ {Path(path).name}"))
