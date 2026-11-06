"""Tự động đưa dữ liệu website (database) vào kho kiến thức của Chatbot.

- Mỗi bản ghi (ngành, điểm chuẩn, học phí, học bổng, FAQ, tin tức...) được chuyển thành văn bản.
- Chỉ tạo embedding cho nội dung MỚI hoặc ĐÃ THAY ĐỔI; nội dung bị xóa sẽ bị gỡ khỏi kho.
- Được gọi tự động khi cán bộ lưu/xóa dữ liệu trong admin (signals), hoặc chạy tay:
      python manage.py sync_knowledge
"""
import hashlib
import logging
import threading

from django.apps import apps
from django.db import models
from django.utils.html import strip_tags

log = logging.getLogger(__name__)

SOURCE_PREFIX = "Website DUE: "

# (model, điều kiện lọc) — chỉ lấy dữ liệu đang hiển thị trên web
SYNC_MODELS = [
    ("NganhDaoTao", {}),
    ("DiemChuan", {}),
    ("PhuongThucXetTuyen", {}),
    ("LoaiHinhDaoTao", {}),
    ("CauHoiThuongGap", {"kich_hoat": True}),
    ("BangHocPhi", {}),
    ("CauHoiHocPhi", {}),
    ("ChinhSachHocBong", {}),
    ("KhoaPhongBan", {}),
    ("ChuyenNganh", {}),
    ("HuongDanNhapHoc", {}),
    ("LichTrinhTanSinhVien", {}),
    ("TinTuc", {}),
]

SKIP_FIELDS = {"id", "slug", "thu_tu", "luot_xem"}
SKIP_TYPES = (models.FileField, models.AutoField, models.BigAutoField, models.JSONField)


def _model(name):
    return apps.get_model("admissions", name)


def _filters_for(model, filters):
    names = {f.name for f in model._meta.get_fields()}
    return {k: v for k, v in filters.items() if k in names}


def _value(obj, field):
    if field.choices:
        return getattr(obj, f"get_{field.name}_display")()
    val = getattr(obj, field.name)
    if val is None or val == "":
        return ""
    if isinstance(field, models.BooleanField):
        return "Có" if val else "Không"
    if isinstance(field, models.TextField):
        return " ".join(strip_tags(str(val)).split())
    return str(val)


def record_to_text(obj):
    meta = obj._meta
    lines = [f"[{meta.verbose_name}] {obj}"]
    for f in meta.concrete_fields:
        if f.name in SKIP_FIELDS or isinstance(f, SKIP_TYPES):
            continue
        v = _value(obj, f)
        if v:
            lines.append(f"{f.verbose_name}: {v}")
    return "\n".join(lines)


def build_texts():
    """Trả về list (source, content) cho toàn bộ dữ liệu website."""
    from .rag import chunk_text
    out = []
    for name, filters in SYNC_MODELS:
        try:
            model = _model(name)
        except LookupError:
            continue
        source = SOURCE_PREFIX + str(model._meta.verbose_name_plural)
        qs = model.objects.filter(**_filters_for(model, filters))
        for obj in qs:
            text = record_to_text(obj)
            for piece in chunk_text(text):  # bài dài (tin tức) được cắt nhỏ
                out.append((source, piece))
    return out


def sync():
    """Đồng bộ kho kiến thức với database. Trả về dict thống kê."""
    from .models import DocumentChunk
    from .rag import embed_texts

    wanted = {}
    for source, content in build_texts():
        key = hashlib.sha1(f"{source}\n{content}".encode("utf-8")).hexdigest()
        wanted[key] = (source, content)

    existing = {}
    stale_ids = []
    for c in DocumentChunk.objects.filter(document__isnull=True, source__startswith=SOURCE_PREFIX):
        key = hashlib.sha1(f"{c.source}\n{c.content}".encode("utf-8")).hexdigest()
        if key in wanted and key not in existing:
            existing[key] = c.id
        else:
            stale_ids.append(c.id)

    new_keys = [k for k in wanted if k not in existing]
    if new_keys:
        vectors = embed_texts([wanted[k][1] for k in new_keys])
        DocumentChunk.objects.bulk_create([
            DocumentChunk(document=None, source=wanted[k][0], chunk_index=i, content=wanted[k][1], embedding=v)
            for i, (k, v) in enumerate(zip(new_keys, vectors))
        ])
    if stale_ids:
        DocumentChunk.objects.filter(id__in=stale_ids).delete()
    return {"tong": len(wanted), "them_moi": len(new_keys), "xoa": len(stale_ids)}


# ---------- Tự đồng bộ khi dữ liệu thay đổi (gộp nhiều lần lưu trong 5 giây) ----------
_timer = None
_lock = threading.Lock()


def _run_sync():
    try:
        stats = sync()
        log.info("Đồng bộ kho kiến thức Chatbot: %s", stats)
    except Exception:
        log.exception("Đồng bộ kho kiến thức Chatbot thất bại")


def schedule_sync(*args, **kwargs):
    global _timer
    with _lock:
        if _timer:
            _timer.cancel()
        _timer = threading.Timer(5.0, _run_sync)
        _timer.daemon = True
        _timer.start()


def connect_signals():
    from django.db.models.signals import post_save, post_delete
    for name, _ in SYNC_MODELS:
        try:
            model = _model(name)
        except LookupError:
            continue
        post_save.connect(schedule_sync, sender=model, dispatch_uid=f"kb_sync_save_{name}")
        post_delete.connect(schedule_sync, sender=model, dispatch_uid=f"kb_sync_delete_{name}")
