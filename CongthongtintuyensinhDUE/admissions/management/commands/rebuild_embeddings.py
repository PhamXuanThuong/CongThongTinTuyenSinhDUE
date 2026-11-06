"""Tạo lại embedding cho TOÀN BỘ kho kiến thức (dùng khi đổi model embedding).

    python manage.py tao_lai_embedding

Giữ nguyên nội dung các đoạn, chỉ tính lại vector bằng model hiện tại trong settings.
"""
from django.core.management.base import BaseCommand
from admissions.models import DocumentChunk
from admissions.rag import embed_texts


class Command(BaseCommand):
    help = "Tạo lại embedding cho toàn bộ kho kiến thức Chatbot"

    def handle(self, *args, **options):
        chunks = list(DocumentChunk.objects.only("id", "content"))
        self.stdout.write(f"Đang tạo lại embedding cho {len(chunks)} đoạn...", ending="\n")
        step = 200
        for i in range(0, len(chunks), step):
            part = chunks[i:i + step]
            vectors = embed_texts([c.content for c in part])
            for c, v in zip(part, vectors):
                c.embedding = v
            DocumentChunk.objects.bulk_update(part, ["embedding"])
            self.stdout.write(f"  {min(i + step, len(chunks))}/{len(chunks)}")
            self.stdout.flush()
        self.stdout.write(self.style.SUCCESS("Xong."))
