"""Bỏ hoàn toàn dữ liệu lấy từ file due_knowledge_base_merged.csv.

- Xóa các đoạn kiến thức nạp trực tiếp từ file CSV (lệnh ingest_knowledge_csv cũ).
- Xóa các câu hỏi đáp trong bảng CauHoiThuongGap (admissions_faq) có mã DUE_KB_..., vốn được nhập từ file này.
  Bảng vẫn được giữ để cán bộ tự thêm câu hỏi mới trong admin.
Sau khi migrate cần chạy: python manage.py sync_knowledge
"""
from django.db import migrations


def remove_csv_data(apps, schema_editor):
    Chunk = apps.get_model("admissions", "DocumentChunk")
    Faq = apps.get_model("admissions", "CauHoiThuongGap")
    Chunk.objects.filter(document__isnull=True, source__contains="due_knowledge_base_merged.csv").delete()
    Faq.objects.filter(ma_cau_hoi__startswith="DUE_KB_").delete()


class Migration(migrations.Migration):
    dependencies = [("admissions", "0009_alter_tailieutuyensinh_file_and_more")]
    operations = [migrations.RunPython(remove_csv_data, migrations.RunPython.noop)]
