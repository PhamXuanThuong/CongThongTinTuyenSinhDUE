"""Đồng bộ tên bảng admissions_* -> tuyensinh_* (theo Meta.db_table trong models.py).

An toàn với mọi trạng thái database:
- DB mới tạo: đổi tên admissions_X thành tuyensinh_X.
- DB đã có sẵn tuyensinh_X (do tạo tay/copy trước đó): giữ nguyên, không đụng tới bảng cũ.
"""
from django.db import migrations

MODELS = [
    'banghocphi', 'cauhoihocphi', 'cauhoithuonggap', 'caulacbo', 'chinhsachhocbong',
    'chuyennganh', 'dangkyclb', 'diemchuan', 'documentchunk', 'hosohuongnghiep',
    'huongdannhaphoc', 'khoaphongban', 'lichtrinhtansinhvien', 'loaihinhdaotao',
    'nganhdaotao', 'phuongthucxettuyen', 'tailieutuyensinh', 'tintuc', 'tuvantuyensinh',
]


def rename_missing_tables(apps, schema_editor):
    existing = set(schema_editor.connection.introspection.table_names())
    for name in MODELS:
        old, new = f'admissions_{name}', f'tuyensinh_{name}'
        if new not in existing and old in existing:
            schema_editor.alter_db_table(None, old, new)


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0005_merge_20261103_1400'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(rename_missing_tables, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AlterModelTable(name=name, table=f'tuyensinh_{name}') for name in MODELS
            ],
        ),
    ]
