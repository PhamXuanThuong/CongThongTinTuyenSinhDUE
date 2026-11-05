import csv
import numpy as np
import requests
from pathlib import Path
from django.conf import settings
from .models import DocumentChunk


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


# ---------- 3. Embedding bằng Ollama ----------
def embed_texts(texts, batch=16):
    out = []
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
def retrieve(query, top_k=None, min_score=None):
    top_k = top_k or settings.RAG_TOP_K
    min_score = settings.RAG_MIN_SCORE if min_score is None else min_score
    rows = list(DocumentChunk.objects.values_list("source", "content", "embedding"))
    if not rows:
        return []
    M = np.array([r[2] for r in rows], dtype=np.float32)
    M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    q = np.array(embed_texts([query])[0], dtype=np.float32)
    q /= (np.linalg.norm(q) + 1e-9)
    scores = M @ q
    idx = np.argsort(-scores)[:top_k]
    return [
        {"source": rows[i][0], "content": rows[i][1], "score": float(scores[i])}
        for i in idx if scores[i] >= min_score
    ]


# ---------- 6. Sinh câu trả lời ----------
SYSTEM_PROMPT = (
    "Bạn là trợ lý tư vấn tuyển sinh của Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE). "
    "Chỉ trả lời dựa trên phần NGỮ CẢNH được cung cấp. "
    "Nếu ngữ cảnh không có thông tin, hãy nói rõ bạn chưa có thông tin và gợi ý liên hệ "
    "hotline 0236 3836 169 hoặc email tuyensinh@due.edu.vn. "
    "Không bịa số liệu, ngày tháng, số điện thoại. Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng."
)

def answer(question, history=None):
    hits = retrieve(question)
    if hits:
        context = "\n\n".join(f"[{i+1}] (Nguồn: {h['source']})\n{h['content']}" for i, h in enumerate(hits))
    else:
        context = "(Không tìm thấy nội dung liên quan)"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in (history or [])[-6:]:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({
        "role": "user",
        "content": f"NGỮ CẢNH:\n{context}\n\nCÂU HỎI: {question}",
    })

    r = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        json={
            "model": settings.OLLAMA_CHAT_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": 8192},
        },
        timeout=600,
    )
    r.raise_for_status()
    reply = r.json()["message"]["content"]
    sources = sorted({h["source"] for h in hits})
    return reply, sources