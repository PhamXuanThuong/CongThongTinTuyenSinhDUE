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

SKIP_FIELDS = {"id", "slug", "thu_tu", "luot_xem", "ngay_tao", "ngay_cap_nhat", "created_at", "updated_at"}
# BooleanField (kich_hoat, noi_bat...) chỉ là cờ quản trị, không mang thông tin cho thí sinh.
# Để lại sẽ sinh nhiễu kiểu "Kích hoạt trợ lý AI / Chatbot: Có" ở mọi đoạn -> chatbot bắt nhầm chữ "AI".
SKIP_TYPES = (models.FileField, models.AutoField, models.BigAutoField, models.JSONField, models.BooleanField)


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


# ---------- App portal: Khoa, Phòng ban, Liên chi đoàn (nhiều cột JSON) ----------
# (model, cột JSON cần đưa vào kiến thức). Các cột giao diện (màu, icon, gallery...) bị bỏ qua.
PORTAL_MODELS = [
    ("Faculty", ["leadership", "departments", "majors_2026", "career_paths", "achievements", "why_choose",
                 "special_programs", "postgraduate", "student_activities", "contact", "lien_chi_doan", "clubs"]),
    ("Department", ["functions", "duties"]),
    ("LienChiDoan", ["executive_board", "featured_activities"]),   # chỉ có ở nhánh develop
    ("HoatDongDoan", []),                                          # chỉ có ở nhánh develop
    ("KyTucXa", []),                                               # chỉ có ở nhánh develop
]
_LABELS = {"name": "Tên", "term": "Nhiệm kỳ", "secretary": "Bí thư", "deputy_secretary": "Phó bí thư",
           "position": "Chức vụ", "title": "Tiêu đề", "date": "Ngày", "desc": "Mô tả", "phone": "Điện thoại",
           "email": "Email", "address": "Địa chỉ", "activities": "Hoạt động", "contact": "Liên hệ"}


def _portal_model(name):
    try:
        return apps.get_model("portal", name)
    except LookupError:
        return None


def _flatten(val, depth=0):
    """Chuyển JSON (dict/list) thành các dòng chữ dễ đọc; bỏ id, url ảnh."""
    if val in (None, "", [], {}):
        return []
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            if k in ("id", "icon", "image", "images", "img", "url", "logo", "color") or v in (None, "", [], {}):
                continue
            sub = _flatten(v, depth + 1)
            if len(sub) == 1:
                lines.append(f"{_LABELS.get(k, k)}: {sub[0]}")
            else:
                lines.append(f"{_LABELS.get(k, k)}:")
                lines.extend("  " + s for s in sub)
        return lines
    if isinstance(val, list):
        out = []
        for item in val:
            sub = _flatten(item, depth + 1)
            if sub:
                out.append("- " + "; ".join(s.strip() for s in sub))
        return out
    return [" ".join(strip_tags(str(val)).split())]


def portal_record_to_text(obj, json_fields):
    lines = [f"[{obj._meta.verbose_name}] {obj}"]
    for f in obj._meta.concrete_fields:
        if f.name in SKIP_FIELDS or isinstance(f, (models.BooleanField, models.AutoField, models.BigAutoField, models.FileField)):
            continue
        if isinstance(f, models.JSONField):
            if f.name not in json_fields:
                continue
            sub = _flatten(getattr(obj, f.name))
            if sub:
                lines.append(f"{f.verbose_name}:")
                lines.extend(sub)
            continue
        if f.name in ("icon", "color", "border_color", "text_color", "light_bg", "gradient", "badge_color", "badge", "order"):
            continue
        v = _value(obj, f)
        if v:
            lines.append(f"{f.verbose_name}: {v}")
    return "\n".join(lines)


def _active(qs):
    names = {f.name for f in qs.model._meta.get_fields()}
    return qs.filter(is_active=True) if "is_active" in names else qs


def build_portal_texts():
    from .rag import chunk_text
    out = []
    for name, json_fields in PORTAL_MODELS:
        model = _portal_model(name)
        if model is None:
            continue
        source = SOURCE_PREFIX + str(model._meta.verbose_name_plural)
        for obj in _active(model.objects.all()):
            for piece in chunk_text(portal_record_to_text(obj, json_fields)):
                out.append((source, piece))

    # Đoạn tổng hợp để trả lời câu hỏi kiểu "có bao nhiêu liên chi đoàn"
    lcd_rows = []
    lcd_model, fac_model = _portal_model("LienChiDoan"), _portal_model("Faculty")
    if lcd_model is not None:
        for o in _active(lcd_model.objects.all()):
            lcd_rows.append((o.name, getattr(o, "faculty_name", ""), getattr(o, "secretary", ""), getattr(o, "term", "")))
    elif fac_model is not None:
        for fac in _active(fac_model.objects.all()):
            for l in (fac.lien_chi_doan or []):
                if isinstance(l, dict) and l.get("name"):
                    lcd_rows.append((l["name"], fac.name, l.get("secretary", ""), l.get("term", "")))
    if lcd_rows:
        lines = [f"[Tổng hợp] Danh sách Liên chi đoàn tại Trường Đại học Kinh tế - ĐH Đà Nẵng",
                 f"Trường hiện có {len(lcd_rows)} Liên chi đoàn trực thuộc các khoa:"]
        for i, (n, fac, sec, term) in enumerate(lcd_rows, 1):
            extra = "; ".join(x for x in (f"thuộc {fac}" if fac else "", f"Bí thư: {sec}" if sec else "", f"Nhiệm kỳ: {term}" if term else "") if x)
            lines.append(f"{i}. {n}" + (f" ({extra})" if extra else ""))
        out.append((SOURCE_PREFIX + "Tổng hợp Liên chi đoàn", "\n".join(lines)))
    return out


def build_texts():
    """Trả về list (source, content) cho toàn bộ dữ liệu website."""
    from .rag import chunk_text
    out = build_portal_texts()
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
    for name, _ in PORTAL_MODELS:
        model = _portal_model(name)
        if model is None:
            continue
        post_save.connect(schedule_sync, sender=model, dispatch_uid=f"kb_sync_save_portal_{name}")
        post_delete.connect(schedule_sync, sender=model, dispatch_uid=f"kb_sync_delete_portal_{name}")
