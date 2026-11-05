"""Tư vấn chọn ngành bằng Gemini: đọc hồ sơ học sinh + danh sách ngành DUE trong DB."""
import json
import time
import requests
from django.conf import settings
from .models import NganhDaoTao

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

HOLLAND_NAMES = {
    'R': 'Kỹ thuật (Realistic)', 'I': 'Nghiên cứu (Investigative)', 'A': 'Nghệ thuật (Artistic)',
    'S': 'Xã hội (Social)', 'E': 'Quản lý/Kinh doanh (Enterprising)', 'C': 'Nghiệp vụ/Chi tiết (Conventional)',
}

SYSTEM_PROMPT = """Bạn là chuyên gia tư vấn hướng nghiệp của Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE).
Nhiệm vụ: dựa trên hồ sơ học sinh (điểm trắc nghiệm Holland RIASEC, sở thích, năng lực, định hướng,
học lực, tổ hợp môn, điều kiện tài chính...) hãy đề xuất 3 đến 5 ngành PHÙ HỢP NHẤT.

QUY TẮC BẮT BUỘC:
- CHỈ tư vấn các ngành của Trường Đại học Kinh tế - Đại học Đà Nẵng. TUYỆT ĐỐI không nhắc tới,
  so sánh hay gợi ý trường đại học nào khác (kể cả các trường thành viên khác của ĐH Đà Nẵng).
- CHỈ chọn ngành có trong DANH SÁCH NGÀNH DUE được cung cấp, giữ nguyên "ma_nganh" và "ten_nganh".
- Nếu học sinh muốn ngành mà DUE không đào tạo (VD: Y, Kỹ thuật, Sư phạm), hãy chọn ngành DUE gần nhất
  với mong muốn đó và giải thích khéo léo trong phần lời khuyên.
- Không bịa điểm chuẩn, học phí; chỉ dùng số liệu có trong danh sách. Nếu "diem_chuan" của ngành là null
  thì được phép dùng điểm chuẩn của chương trình CÙNG NGÀNH (cùng 7 số đầu của mã) có trong danh sách,
  nhưng BẮT BUỘC ghi rõ là tham khảo, theo mẫu: "Chương trình này chưa có điểm chuẩn riêng; tham khảo
  điểm chuẩn ngành <tên> (<mã>) năm <năm>: <điểm>". Nếu cả ngành đều không có điểm thì ghi
  "Chưa có dữ liệu điểm chuẩn" và không nêu con số nào. Không bao giờ dùng số ngoài danh sách.
- Khi có nhiều chương trình cùng ngành, ưu tiên chương trình CÓ điểm chuẩn để học sinh dễ so sánh.
- Cân nhắc cả tính cách lẫn nguyện vọng; nếu điểm dự kiến thấp hơn điểm chuẩn thì nêu rõ mức độ cạnh tranh
  và gợi ý phương án an toàn hơn.
- Viết tiếng Việt, xưng "em" với học sinh, giọng thân thiện, cụ thể, không chung chung.
- Trả về đúng JSON theo schema, sắp xếp từ phù hợp nhất."""

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "tong_quan": {"type": "STRING", "description": "2-4 câu nhận xét tổng quan về tính cách và định hướng của học sinh"},
        "nganh_de_xuat": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "ma_nganh": {"type": "STRING"},
                    "ten_nganh": {"type": "STRING"},
                    "muc_do_phu_hop": {"type": "INTEGER", "description": "0-100"},
                    "ly_do": {"type": "STRING", "description": "Vì sao phù hợp với em, 2-3 câu"},
                    "kha_nang_trung_tuyen": {"type": "STRING", "description": "Nhận xét ngắn so với điểm chuẩn"},
                },
                "required": ["ma_nganh", "ten_nganh", "muc_do_phu_hop", "ly_do"],
            },
        },
        "loi_khuyen": {"type": "STRING", "description": "Lời khuyên chọn phương án/nguyện vọng, 2-4 câu"},
    },
    "required": ["tong_quan", "nganh_de_xuat", "loi_khuyen"],
}


def _majors_catalog():
    """Danh sách ngành DUE kèm điểm chuẩn mới nhất, lấy từ database."""
    catalog = {}
    for n in NganhDaoTao.objects.prefetch_related('diem_chuan_cac_nam').all():
        diem = sorted(n.diem_chuan_cac_nam.all(), key=lambda d: -d.nam)
        latest = {}
        for d in diem:
            if d.nam == diem[0].nam:
                latest[d.get_phuong_thuc_display()] = float(d.diem_trung_tuyen)
        catalog[n.ma_nganh] = {
            "ma_nganh": n.ma_nganh,
            "ten_nganh": n.ten_nganh,
            "khoa": n.khoa,
            "to_hop": n.to_hop_mon,
            "hoc_phi": n.hoc_phi_du_kien,
            "chi_tieu": n.chi_tieu,
            "mo_ta": (n.mo_ta or "")[:400],
            "diem_chuan": {"nam": diem[0].nam, **latest} if diem else None,
        }
    return catalog


def _build_prompt(profile, scores, holland_code, catalog):
    score_txt = ", ".join(f"{k} - {HOLLAND_NAMES[k]}: {v}" for k, v in scores.items())
    profile_txt = "\n".join(f"- {k}: {v}" for k, v in profile.items() if v)
    majors_txt = json.dumps(list(catalog.values()), ensure_ascii=False)
    return (
        f"HỒ SƠ HỌC SINH:\n{profile_txt}\n\n"
        f"ĐIỂM HOLLAND: {score_txt}\nMã Holland top 3: {holland_code or 'chưa xác định'}\n\n"
        f"DANH SÁCH NGÀNH DUE:\n{majors_txt}"
    )


def _call_gemini(prompt):
    from .rag import gemini_generate  # dùng chung cơ chế model dự phòng với chatbot
    text, _ = gemini_generate(settings.GEMINI_ADVISOR_MODEL, {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    })
    return text


def _to_json_schema(s):
    """Chuyển schema kiểu Gemini (type viết hoa) sang JSON Schema chuẩn cho Ollama."""
    out = {k: v for k, v in s.items() if k not in ("type", "properties", "items")}
    out["type"] = s["type"].lower()
    if "properties" in s:
        out["properties"] = {k: _to_json_schema(v) for k, v in s["properties"].items()}
    if "items" in s:
        out["items"] = _to_json_schema(s["items"])
    return out


def _call_ollama(prompt):
    r = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        json={
            "model": settings.OLLAMA_CHAT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "format": _to_json_schema(RESPONSE_SCHEMA),
            "stream": False,
            "options": {"temperature": 0.3, "num_ctx": 16384},
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]


def analyze(profile, scores, holland_code):
    """Trả về dict kết quả AI, hoặc raise nếu không gọi được AI.
    Dùng Gemini nếu có GEMINI_API_KEY, ngược lại dùng Ollama local."""
    catalog = _majors_catalog()
    if not catalog:
        raise RuntimeError("Chưa có dữ liệu ngành trong database")

    prompt = _build_prompt(profile, scores, holland_code, catalog)
    text = _call_gemini(prompt) if settings.GEMINI_API_KEY else _call_ollama(prompt)
    result = json.loads(text)

    # Chỉ giữ ngành có thật trong DB, bổ sung thông tin khoa/điểm chuẩn từ DB
    majors = []
    for m in result.get("nganh_de_xuat", []):
        info = catalog.get(str(m.get("ma_nganh", "")).strip())
        if not info:
            continue
        dc = info["diem_chuan"] or {}
        thpt = "Điểm thi tốt nghiệp THPT"
        diem_ten, diem = (thpt, dc[thpt]) if thpt in dc else next(
            ((k, v) for k, v in dc.items() if k != "nam"), (None, None))
        majors.append({
            "ma": info["ma_nganh"],
            "ten": " ".join(info["ten_nganh"].split()).rstrip(":"),
            "phuong_thuc_diem": diem_ten if diem_ten != thpt else "",
            "khoa": info["khoa"],
            "to_hop": info["to_hop"],
            "diem": f"{diem:.2f}" if diem is not None else "—",
            "nam_diem": dc.get("nam"),
            "phu_hop": max(0, min(100, int(m.get("muc_do_phu_hop", 0)))),
            "ly_do": m.get("ly_do", ""),
            "kha_nang": m.get("kha_nang_trung_tuyen", ""),
        })
    if not majors:
        raise RuntimeError("AI không trả về ngành hợp lệ")
    return {
        "tong_quan": result.get("tong_quan", ""),
        "loi_khuyen": result.get("loi_khuyen", ""),
        "majors": majors[:5],
    }
