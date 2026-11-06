import csv
import json
import logging
import math
import re
import time
import numpy as np
import requests
from pathlib import Path
from django.conf import settings
from .models import DocumentChunk

log = logging.getLogger(__name__)


# ---------- 1. Đọc nội dung file ----------
def extract_text(path):
    ext = Path(path).suffix.lower()
    if ext in (".txt", ".md"):
        return Path(path).read_text(encoding="utf-8-sig", errors="ignore")
    if ext == ".pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if ext == ".docx":
        from docx import Document
        d = Document(path)
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                parts.append(" | ".join(c.text.strip() for c in row.cells))
        return "\n".join(parts)
    if ext == ".csv":
        with open(path, encoding="utf-8-sig", errors="ignore", newline="") as f:
            return "\n".join(
                " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                for row in csv.DictReader(f)
            )
    if ext == ".xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(path, data_only=True, read_only=True)
        lines = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                cells = [str(c) for c in row if c is not None]
                if cells:
                    lines.append(" | ".join(cells))
        return "\n".join(lines)
    raise ValueError(f"Định dạng {ext} chưa được hỗ trợ")


# ---------- 2. Cắt đoạn ----------
def chunk_text(text, size=None, overlap=None):
    size = size or settings.RAG_CHUNK_SIZE
    overlap = overlap or settings.RAG_CHUNK_OVERLAP
    text = "\n".join(l.strip() for l in text.splitlines() if l.strip())
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):  # cố gắng ngắt ở cuối dòng/câu
            cut = max(text.rfind("\n", start, end), text.rfind(". ", start, end))
            if cut > start + size // 2:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


# ---------- 3. Embedding (Gemini nếu có key, ngược lại Ollama) ----------
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _use_gemini():
    return bool(settings.GEMINI_API_KEY)


def _gemini_post(path, payload, timeout=120, attempts=3, wait_429=2):
    for attempt in range(attempts):  # 429/500/503 -> thử lại
        r = requests.post(
            f"{GEMINI_BASE}/{path}",
            headers={"x-goog-api-key": settings.GEMINI_API_KEY, "Content-Type": "application/json"},
            json=payload, timeout=timeout,
        )
        if r.status_code not in (429, 500, 503) or attempt == attempts - 1:
            break
        time.sleep(wait_429 if r.status_code == 429 else 2 * (attempt + 1))
    r.raise_for_status()
    return r.json()


def gemini_generate(model, payload):
    """Gọi generateContent; model chính quá tải/treo/hết hạn mức thì thử lần lượt các model dự phòng.
    Trả về (text, model_đã_dùng)."""
    models = [model] + [m for m in settings.GEMINI_FALLBACK_MODELS if m != model]
    last_err = None
    for m in models:
        try:
            data = _gemini_post(f"{m}:generateContent", payload, timeout=settings.GEMINI_TIMEOUT, attempts=1)
            return data["candidates"][0]["content"]["parts"][0]["text"], m
        except Exception as e:  # timeout, 429, 5xx, model không tồn tại...
            last_err = e
            log.warning("Gemini model %s lỗi (%s) -> thử model dự phòng", m, e)
    raise last_err


def embed_texts(texts, batch=None, task="RETRIEVAL_DOCUMENT"):
    out = []
    if _use_gemini():
        model = settings.GEMINI_EMBED_MODEL
        # Gói miễn phí: tối đa 100 đoạn/phút -> gửi lô 90, bị giới hạn thì chờ 1 phút
        batch = batch or 40
        for i in range(0, len(texts), batch):
            if i:  # giãn cách các lô để không vượt hạn mức/phút của gói miễn phí
                time.sleep(20)
            data = _gemini_post(f"{model}:batchEmbedContents", {"requests": [
                {"model": f"models/{model}", "content": {"parts": [{"text": t}]},
                 "taskType": task, "outputDimensionality": settings.GEMINI_EMBED_DIM}
                for t in texts[i:i + batch]
            ]}, attempts=6 if len(texts) > 1 else 1, wait_429=62)  # câu hỏi lẻ: lỗi thì tìm từ khóa ngay
            out.extend(e["values"] for e in data["embeddings"])
        return out
    batch = batch or 16
    for i in range(0, len(texts), batch):
        r = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/embed",
            json={"model": settings.OLLAMA_EMBED_MODEL, "input": texts[i:i + batch]},
            timeout=600,
        )
        r.raise_for_status()
        out.extend(r.json()["embeddings"])
    return out


# ---------- 4. Lập chỉ mục ----------
def index_document(doc):
    """doc: TaiLieuTuyenSinh"""
    DocumentChunk.objects.filter(document=doc).delete()
    text = extract_text(doc.file.path)
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Không trích xuất được nội dung (file scan ảnh?)")
    vectors = embed_texts(chunks)
    DocumentChunk.objects.bulk_create([
        DocumentChunk(document=doc, source=doc.title, chunk_index=i, content=c, embedding=v)
        for i, (c, v) in enumerate(zip(chunks, vectors))
    ])
    doc.is_processed = True
    doc.save(update_fields=["is_processed"])
    return len(chunks)


def index_csv_rows(path):
    """Mỗi dòng CSV = 1 chunk (dùng cho file kiến thức có sẵn)."""
    source = Path(path).name
    DocumentChunk.objects.filter(document__isnull=True, source=source).delete()
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    texts = [
        "\n".join(f"{k}: {v}" for k, v in r.items() if v and v.strip())
        for r in rows
    ]
    vectors = embed_texts(texts)
    DocumentChunk.objects.bulk_create([
        DocumentChunk(document=None, source=source, chunk_index=i, content=t, embedding=v)
        for i, (t, v) in enumerate(zip(texts, vectors))
    ])
    return len(texts)


# ---------- 5. Truy xuất ----------
# Tách riêng số và chữ để "7310101ST" vẫn khớp với "7310101"
_WORD = re.compile(r"\d+|[a-zà-ỹđ]+", re.IGNORECASE)


def _keyword_retrieve(query, top_k):
    """Tìm theo từ khóa (BM25 rút gọn) — dùng khi không gọi được embedding (hết hạn mức, mất mạng)."""
    q_terms = set(_WORD.findall(query.lower()))
    if not q_terms:
        return []
    rows = list(DocumentChunk.objects.values_list("source", "content"))
    docs = [_WORD.findall(c.lower()) for _, c in rows]
    n = len(docs) or 1
    avg = sum(len(d) for d in docs) / n or 1
    df = {t: sum(1 for d in docs if t in d) for t in q_terms}
    scored = []
    for (src, content), words in zip(rows, docs):
        if not words:
            continue
        tf = {}
        for w in words:
            if w in q_terms:
                tf[w] = tf.get(w, 0) + 1
        if not tf:
            continue
        s = sum(math.log(1 + (n - df[t] + .5) / (df[t] + .5)) * f * 2.2 / (f + 1.2 * (.25 + .75 * len(words) / avg))
                for t, f in tf.items())
        scored.append((s, src, content))
    scored.sort(key=lambda x: -x[0])
    return [{"source": s, "content": c, "score": float(sc)} for sc, s, c in scored[:top_k]]


def retrieve(query, top_k=None, min_score=None):
    top_k = top_k or settings.RAG_TOP_K
    min_score = settings.RAG_MIN_SCORE if min_score is None else min_score
    try:
        q = np.array(embed_texts([query], task="RETRIEVAL_QUERY")[0], dtype=np.float32)
    except Exception as e:
        log.warning("Embedding lỗi (%s) -> chuyển sang tìm theo từ khóa", e)
        return _keyword_retrieve(query, top_k)
    # Chỉ so với các đoạn được tạo bằng cùng model embedding (cùng số chiều)
    rows = [r for r in DocumentChunk.objects.values_list("source", "content", "embedding")
            if len(r[2]) == len(q)]
    if not rows:
        return []
    M = np.array([r[2] for r in rows], dtype=np.float32)
    M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    q /= (np.linalg.norm(q) + 1e-9)
    scores = M @ q
    idx = np.argsort(-scores)[:top_k]
    hits = [
        {"source": rows[i][0], "content": rows[i][1], "score": float(scores[i])}
        for i in idx if scores[i] >= min_score
    ]
    # Tìm kết hợp: embedding bắt theo nghĩa, từ khóa bắt chính xác mã ngành / con số / tên riêng
    seen = {h["content"] for h in hits}
    for h in _keyword_retrieve(query, max(3, top_k // 2)):
        if h["content"] not in seen:
            seen.add(h["content"])
            hits.append({**h, "score": min_score})
    return hits


# ---------- 6. Sinh câu trả lời ----------
SYSTEM_PROMPT = (
    "Bạn là trợ lý tư vấn tuyển sinh của Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE). "
    "CHỈ trả lời dựa trên phần NGỮ CẢNH được cung cấp, không dùng kiến thức bên ngoài. "
    "Không bịa số liệu, ngày tháng, điểm chuẩn, học phí, số điện thoại. "
    "Không tư vấn về trường đại học khác. "
    "THỨ TỰ ƯU TIÊN NGUỒN: các đoạn có nhãn [ƯU TIÊN 1] (tài liệu tuyển sinh chính thức và câu trả lời "
    "của cán bộ) luôn đúng hơn các đoạn [ƯU TIÊN 2] (dữ liệu website). Nếu hai nguồn mâu thuẫn "
    "(mã ngành, chỉ tiêu, điểm chuẩn, học phí, số điện thoại...) thì dùng số liệu [ƯU TIÊN 1]; "
    "chỉ dùng [ƯU TIÊN 2] để bổ sung chi tiết mà [ƯU TIÊN 1] không có. "
    "Nếu NGỮ CẢNH không đủ thông tin để trả lời chính xác câu hỏi thì đặt co_thong_tin = false "
    "(câu hỏi sẽ được chuyển cho cán bộ tuyển sinh). "
    "Với lời chào hỏi xã giao (xin chào, cảm ơn...) thì trả lời thân thiện và đặt co_thong_tin = true. "
    "Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng. Khi liệt kê, MỖI Ý PHẢI NẰM TRÊN MỘT DÒNG RIÊNG, "
    "bắt đầu bằng '- ' (dùng ký tự xuống dòng \\n giữa các ý); dùng **chữ đậm** cho con số/từ khóa quan trọng."
)

ANSWER_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "co_thong_tin": {"type": "BOOLEAN", "description": "Ngữ cảnh có đủ thông tin để trả lời không"},
        "tra_loi": {"type": "STRING"},
    },
    "required": ["co_thong_tin", "tra_loi"],
}


def _compress_history(history, max_turns=6, max_chars=3000):
    """
    Nén ngữ cảnh hội thoại khi phiên chat quá dài:
    - Nếu lịch sử ngắn (<= max_turns): Giữ nguyên.
    - Nếu lịch sử dài (> max_turns): Tóm tắt các lượt trao đổi cũ hơn thành 1 bản tóm tắt súc tích,
      và chỉ giữ nguyên vẹn các lượt hội thoại gần nhất.
    """
    if not history:
        return []

    valid_msgs = [m for m in history if m.get("role") in ("user", "assistant") and m.get("content")]
    if len(valid_msgs) <= max_turns:
        return valid_msgs

    # Tách thành: các tin nhắn cũ cần tóm tắt và các tin nhắn gần nhất
    older = valid_msgs[:-max_turns]
    recent = valid_msgs[-max_turns:]

    # Tạo tóm tắt cô đọng cho các tin cũ
    summary_lines = []
    for m in older:
        speaker = "Thí sinh" if m["role"] == "user" else "Tư vấn"
        content = m["content"].strip().replace("\n", " ")
        # Cắt ngắn mỗi câu cũ tối đa 120 ký tự để tiết kiệm context
        if len(content) > 120:
            content = content[:117] + "..."
        summary_lines.append(f"- {speaker}: {content}")

    compressed_summary = "[TÓM TẮT HỘI THOẠI TRƯỚC ĐÓ]:\n" + "\n".join(summary_lines)
    if len(compressed_summary) > max_chars:
        compressed_summary = compressed_summary[:max_chars - 3] + "..."

    # Ghép lại: 1 thông điệp tóm tắt của user + các tin nhắn gần nhất
    return [{"role": "user", "content": compressed_summary}] + recent


def _build_messages(question, history, context):
    compressed_history = _compress_history(history)
    turns = []
    for m in compressed_history:
        turns.append((m["role"], m["content"]))
    turns.append(("user", f"NGỮ CẢNH TÀI LIỆU:\n{context}\n\nCÂU HỎI HIỆN TẠI: {question}"))
    return turns


def answer(question, history=None):
    """Trả về (reply, sources, found). found=False nghĩa là cần chuyển cho cán bộ."""
    hits = retrieve(question)
    # Tài liệu (CSV, file upload) và câu trả lời của cán bộ được ưu tiên hơn dữ liệu website (DB)
    def _priority(h):
        return 2 if h["source"].startswith("Website DUE:") else 1
    hits.sort(key=lambda h: (_priority(h), -h["score"]))
    # Đã có đủ tài liệu ưu tiên 1 thì bỏ hẳn dữ liệu website để AI không lẫn số liệu mâu thuẫn
    if sum(1 for h in hits if _priority(h) == 1) >= 2:
        hits = [h for h in hits if _priority(h) == 1]
    if hits:
        context = "\n\n".join(
            f"[{i+1}] [ƯU TIÊN {_priority(h)}] (Nguồn: {h['source']})\n{h['content']}" for i, h in enumerate(hits))
    else:
        context = "(Không tìm thấy nội dung liên quan)"
    turns = _build_messages(question, history, context)

    if _use_gemini():
        text, _ = gemini_generate(settings.GEMINI_CHAT_MODEL, {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "model" if r == "assistant" else "user", "parts": [{"text": t}]} for r, t in turns],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json",
                                 "responseSchema": ANSWER_SCHEMA},
        })
        result = json.loads(text)
    else:
        r = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.OLLAMA_CHAT_MODEL,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] +
                            [{"role": role, "content": t} for role, t in turns],
                "format": {"type": "object", "properties": {"co_thong_tin": {"type": "boolean"},
                           "tra_loi": {"type": "string"}}, "required": ["co_thong_tin", "tra_loi"]},
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 8192},
            },
            timeout=600,
        )
        r.raise_for_status()
        result = json.loads(r.json()["message"]["content"])

    found = bool(result.get("co_thong_tin"))
    sources = sorted({h["source"] for h in hits}) if found else []
    return result.get("tra_loi", ""), sources, found


def add_knowledge(question, answer_text, source="Cán bộ tuyển sinh trả lời"):
    """Lưu một cặp hỏi-đáp do cán bộ viết vào kho kiến thức của chatbot."""
    content = f"Câu hỏi: {question}\nTrả lời: {answer_text}"
    vec = embed_texts([content])[0]
    idx = DocumentChunk.objects.filter(document__isnull=True, source=source).count()
    DocumentChunk.objects.create(document=None, source=source, chunk_index=idx, content=content, embedding=vec)
