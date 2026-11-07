# Tài liệu Chatbot tư vấn tuyển sinh DUE

> Tài liệu này mô tả **logic hiện tại** của chatbot. Mỗi khi sửa code chatbot (xem mục 9) phải cập nhật lại tài liệu này.
> Cập nhật lần cuối: 07/11/2026.

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Nguồn kiến thức](#2-nguồn-kiến-thức)
3. [Luồng trả lời một câu hỏi](#3-luồng-trả-lời-một-câu-hỏi)
4. [Nguyên tắc trả lời (không trả lời bừa)](#4-nguyên-tắc-trả-lời-không-trả-lời-bừa)
5. [Chuyển câu hỏi cho cán bộ](#5-chuyển-câu-hỏi-cho-cán-bộ)
6. [Cập nhật kiến thức](#6-cập-nhật-kiến-thức)
7. [Cấu hình](#7-cấu-hình)
8. [API và giao diện](#8-api-và-giao-diện)
9. [Bản đồ file code](#9-bản-đồ-file-code)
10. [Xử lý sự cố thường gặp](#10-xử-lý-sự-cố-thường-gặp)
11. [Bộ test kiểm tra nhanh](#11-bộ-test-kiểm-tra-nhanh)

---

## 1. Tổng quan

Chatbot hoạt động theo mô hình **RAG** (Retrieval-Augmented Generation):

- Chatbot **không đọc trực tiếp** database hay file mỗi lần trả lời.
- Mọi kiến thức được cắt thành các **đoạn nhỏ**, chuyển thành **vector** (embedding) và lưu sẵn vào **kho kiến thức** — bảng `admissions_document_chunk`.
- Mỗi câu hỏi, hệ thống tìm vài đoạn liên quan nhất trong kho rồi đưa cho **Gemini** đọc và viết câu trả lời.

```
Nguồn kiến thức ──(nạp / đồng bộ)──► KHO KIẾN THỨC (admissions_document_chunk) ──(tìm kiếm)──► Gemini ──► Câu trả lời
```

---

## 2. Nguồn kiến thức

| # | Nguồn | Nội dung | Cách vào kho | Ưu tiên |
|---|---|---|---|---|
| ① | **File CSV kiến thức** `CongthongtintuyensinhDUE/data/due_knowledge_base_merged.csv` | ~221 chủ đề tuyển sinh 2026 (→ ~332 đoạn) | Lệnh `ingest_knowledge_csv` | **1** |
| ② | **Tệp cán bộ tải lên** (mục *Tài liệu tư vấn* ở `/chatbot/`) | PDF, DOCX, XLSX, CSV, TXT, MD | **Tự động** khi tải lên; xóa tệp thì kiến thức của tệp cũng bị xóa | **1** |
| ③ | **Câu trả lời của cán bộ** (tích “Thêm vào kho kiến thức”) | Cặp hỏi – đáp | **Tự động** | **1** |
| ④ | **Dữ liệu website trong database** | Xem danh sách bên dưới | **Tự động** khi sửa qua admin; hoặc lệnh `sync_knowledge` | 2 |

Nguồn ④ được đánh dấu `source` bắt đầu bằng `"Website DUE: "`; các nguồn còn lại là ưu tiên 1.

### Các bảng database đang được đồng bộ (nguồn ④)

Khai báo trong `admissions/knowledge_sync.py`:

- **`SYNC_MODELS`** (app `admissions`): Ngành đào tạo, Điểm chuẩn, Phương thức xét tuyển, Loại hình đào tạo, Câu hỏi thường gặp (đang kích hoạt), Bảng học phí, FAQ học phí, Chính sách học bổng, Khoa & phòng ban, Chuyên ngành, Hướng dẫn nhập học, Lịch trình tân sinh viên, Tin tức.
- **`PORTAL_MODELS`** (app `portal`): Khoa/Viện (kèm ban lãnh đạo, bộ môn, ngành, liên chi đoàn, CLB, liên hệ…), Phòng ban. Nếu code có các model `LienChiDoan`, `HoatDongDoan`, `KyTucXa` thì cũng được đồng bộ.
- Thêm 1 đoạn **tổng hợp “Danh sách Liên chi đoàn”** để trả lời câu hỏi số lượng.

Quy tắc chuyển bản ghi thành văn bản:
- Bỏ các cột không mang thông tin: `id`, `slug`, `thu_tu`, `luot_xem`, ngày tạo/cập nhật, cột `BooleanField` (ví dụ `kich_hoat`), cột file.
- Cột JSON của app `portal` được chuyển thành các dòng “Nhãn: giá trị” (bỏ id, ảnh, màu, icon).
- Bài dài được cắt nhỏ theo `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP`.

> **Thêm bảng mới mà muốn chatbot biết:** thêm vào `SYNC_MODELS` (app admissions) hoặc `PORTAL_MODELS` (app portal), rồi chạy `python manage.py sync_knowledge`. Không làm bước này thì dữ liệu có trong database nhưng chatbot **không biết**.

---

## 3. Luồng trả lời một câu hỏi

Hàm chính: `rag.answer(question, history)` — gọi từ API `POST /api/chat/` (`views.api_chat`).

1. **Lưu tin nhắn** vào `ChatSession` / `ChatMessage`, nạp lịch sử hội thoại; lịch sử dài được nén (`_compress_history`: giữ nguyên 6 lượt gần nhất, tóm tắt phần cũ).
2. **Tìm tài liệu** (`rag.retrieve`):
   - **Theo nghĩa**: tạo embedding câu hỏi, so cosine với các đoạn trong kho, lấy `RAG_TOP_K` (8) đoạn có điểm ≥ `RAG_MIN_SCORE` (0.35). Chỉ so với đoạn có cùng số chiều vector.
   - **Theo từ khóa** (BM25 rút gọn, `_keyword_retrieve`): bổ sung đoạn khớp chính xác mã ngành, con số, tên riêng.
     - Bỏ ~100 từ phổ biến / viết tắt khi chat (`_STOPWORDS`: có, ai, k, v, ko, j, gì, là…).
     - Câu có ≤ 2 từ có nghĩa: phải khớp hết; câu dài hơn: khớp ≥ 2 từ, hoặc khớp 1 mã số ≥ 4 chữ số.
   - Hết hạn mức / lỗi embedding → chỉ dùng tìm theo từ khóa.
3. **Xếp ưu tiên**: đoạn ưu tiên 1 lên trước. Nếu có ≥ 2 đoạn ưu tiên 1 thì **bỏ hẳn** đoạn ưu tiên 2 (tránh lẫn số liệu mâu thuẫn).
4. **Gọi Gemini** (`GEMINI_CHAT_MODEL`) với `SYSTEM_PROMPT` + ngữ cảnh (mỗi đoạn có nhãn `[ƯU TIÊN 1|2]` và nguồn) + lịch sử. Bắt buộc trả về JSON:
   ```json
   { "ngoai_pham_vi": false, "co_thong_tin": true, "tra_loi": "..." }
   ```
   Model chính lỗi / treo quá `GEMINI_TIMEOUT` giây → tự thử lần lượt `GEMINI_FALLBACK_MODELS`.
5. **Quyết định** (trong code, không chỉ dựa vào AI):
   - `co_thong_tin = true` **và** có câu trả lời **và** có ít nhất 1 đoạn tài liệu **và** `ngoai_pham_vi = false` → trả lời kèm nguồn.
   - **Mọi trường hợp còn lại** (không có tài liệu, AI đánh giá không đủ thông tin, câu ngoài phạm vi / chào hỏi / tán gẫu, AI lỗi) → **chuyển cán bộ** (mục 5). AI không được tự viết câu trả lời cho các câu này.

---

## 4. Nguyên tắc trả lời (không trả lời bừa)

| Tình huống | Chatbot làm gì |
|---|---|
| Có tài liệu trả lời **trực tiếp** câu hỏi | Trả lời dựa trên tài liệu, kèm nguồn |
| Không có tài liệu liên quan / tài liệu không trả lời được | **Chuyển cán bộ** |
| Chào hỏi, tán gẫu, câu nhạy cảm, nhờ làm bài, kiến thức chung | **Chuyển cán bộ** (AI đánh dấu `ngoai_pham_vi`, không tự trả lời) |
| AI lỗi / hết hạn mức | Chuyển cán bộ; **không bao giờ** hiển thị tài liệu thô |

Prompt (`SYSTEM_PROMPT` trong `rag.py`) yêu cầu AI:
- Chỉ dùng ngữ cảnh, không dùng kiến thức bên ngoài; không bịa số liệu, ngày, học phí, số điện thoại.
- Không tư vấn trường khác.
- Đánh giá đoạn tài liệu có trả lời **trực tiếp** không; không lấy đại đoạn gần giống.
- Không chép nguyên văn ngữ cảnh, không liệt kê tên trường dữ liệu.
- Ưu tiên nguồn `[ƯU TIÊN 1]` khi mâu thuẫn.
- Liệt kê mỗi ý một dòng, dùng **chữ đậm** cho số liệu.

---

## 5. Chuyển câu hỏi cho cán bộ

| Người hỏi | Kết quả |
|---|---|
| **Chưa đăng nhập** | Hiện hướng dẫn đăng nhập / gọi hotline (`UNAUTH_HANDOFF_REPLY`); câu hỏi **không** vào hàng chờ (chống spam) |
| **Đã đăng nhập** | Lưu vào `admissions_pending_question` (`CauHoiChoTraLoi`), hiện `HANDOFF_REPLY`; khung chat kiểm tra câu trả lời mỗi 5 giây |

Cán bộ trả lời tại `/can-bo/hoi-dap/` (chỉ tài khoản staff). Tích **“Thêm vào kho kiến thức”** → `rag.add_knowledge()` lưu cặp hỏi – đáp vào kho (nguồn “Cán bộ tuyển sinh trả lời”, ưu tiên 1).

---

## 6. Cập nhật kiến thức

| Thay đổi | Tự động? | Cần làm |
|---|---|---|
| Sửa dữ liệu qua **admin** (bảng trong `SYNC_MODELS` / `PORTAL_MODELS`) | ✅ sau ~5 giây | — |
| **Tải tệp** ở mục Tài liệu tư vấn | ✅ | Thay tệp: xóa tệp cũ trước rồi tải bản mới |
| **Xóa tệp** ở mục Tài liệu tư vấn | ✅ | Kiến thức của tệp đó bị xóa khỏi kho ngay |
| Cán bộ trả lời + tích “Thêm vào kho” | ✅ | — |
| Sửa **trực tiếp database** (DB Browser, SQL) | ❌ | `python manage.py sync_knowledge` |
| Sửa **file CSV** kiến thức | ❌ | `python manage.py ingest_knowledge_csv data/due_knowledge_base_merged.csv` |
| **Thêm bảng mới** muốn chatbot biết | ❌ | Thêm vào `SYNC_MODELS` / `PORTAL_MODELS` trong `admissions/knowledge_sync.py`, rồi `python manage.py sync_knowledge` |
| Đổi **model embedding** | ❌ | `python manage.py rebuild_embeddings` |
| **Đổi logic đồng bộ** (`knowledge_sync.py`) | ❌ | `python manage.py sync_knowledge` trên mọi máy |
| **Pull code mới** có sửa phần đồng bộ (ví dụ sau khi merge PR chatbot) | ❌ | `python manage.py sync_knowledge` một lần trên máy mình |
| Nạp dữ liệu hàng loạt bằng lệnh **seed** (`seed_portal_data`, `seed_data`…) hoặc script | ⚠️ Không chắc | Chạy thêm `python manage.py sync_knowledge` (xem lưu ý bên dưới) |

> **Vì sao sau lệnh seed phải chạy `sync_knowledge`:** tự đồng bộ chờ ~5 giây sau lần lưu cuối mới chạy (để gộp nhiều lần lưu). Lệnh seed chạy xong thoát ngay nên việc đồng bộ thường bị hủy. Ngoài ra `bulk_create` / `update()` / sửa thẳng SQL **không phát tín hiệu** nên không bao giờ tự đồng bộ.

### 6.1. Thêm bảng dữ liệu mới cho chatbot (tránh lỗi như “Liên chi đoàn”)

**Bài học:** dữ liệu Liên chi đoàn đã có trong database (bảng Khoa, app `portal`) nhưng chatbot không trả lời được, vì bảng đó **chưa có trong danh sách đồng bộ** và nằm trong cột JSON mà phần đồng bộ cũ bỏ qua. **Có dữ liệu trong database ≠ chatbot biết.**

Mỗi khi tạo **bảng (model) mới** chứa thông tin muốn chatbot trả lời, làm đủ các bước:

1. **Khai báo bảng** trong `admissions/knowledge_sync.py`:
   - Model của app `admissions` → thêm vào `SYNC_MODELS`: `("TenModel", {})` (có thể thêm điều kiện lọc, ví dụ `{"kich_hoat": True}`).
   - Model của app `portal` (hoặc app khác có nhiều cột JSON) → thêm vào `PORTAL_MODELS`: `("TenModel", ["cot_json_1", "cot_json_2"])` — liệt kê các cột JSON **có nội dung cho thí sinh** (bỏ cột ảnh, màu, icon).
   - App khác ngoài `admissions` / `portal`: cần sửa thêm hàm `_model` / `_portal_model` để lấy đúng app.
2. **Đặt `verbose_name` tiếng Việt** cho model và các cột: tên này được ghi vào kiến thức (ví dụ “Bí thư: …”), đặt rõ nghĩa thì AI tìm và trả lời tốt hơn.
3. Nếu thí sinh hay hỏi **câu tổng hợp** (“có bao nhiêu…”, “danh sách…”), thêm một **đoạn tổng hợp** như đoạn “Danh sách Liên chi đoàn” trong `build_portal_texts()`.
4. **Chạy** `python manage.py sync_knowledge` và **hỏi thử** 2–3 câu về bảng mới (một câu chi tiết, một câu tổng hợp).
5. **Cập nhật tài liệu này** (mục 2 – danh sách bảng, mục 11 – thêm câu test) và ghi trong mô tả PR: “sau khi merge cần chạy `sync_knowledge`”.

Kiểm tra nhanh bảng nào **chưa** được đồng bộ:

```powershell
python manage.py shell -c "from django.apps import apps; from admissions.knowledge_sync import SYNC_MODELS, PORTAL_MODELS; s={n for n,_ in SYNC_MODELS+PORTAL_MODELS}; print([m.__name__ for a in ('admissions','portal') for m in apps.get_app_config(a).get_models() if m.__name__ not in s])"
```

Danh sách in ra gồm cả bảng hệ thống của chatbot (`DocumentChunk`, `ChatSession`…) — chỉ cần xem có bảng **dữ liệu cho thí sinh** nào bị sót (ví dụ hiện tại: `CauLacBo` – CLB chưa được đồng bộ riêng).

Chạy lệnh trong thư mục `CongthongtintuyensinhDUE` (có `manage.py`), đã kích hoạt `.venv`.

Chi phí embedding: `sync_knowledge` chỉ embed phần **thay đổi**; `ingest_knowledge_csv` embed lại toàn bộ file (~332 lượt); `rebuild_embeddings` embed toàn kho (~1.200 lượt). Gói miễn phí: ~1.000 lượt/ngày, 100 lượt/phút (lệnh tự chia lô 40 và chờ khi bị giới hạn).

> `db.sqlite3` **không lưu trên git**. Mỗi máy tự giữ database (kho kiến thức nằm trong đó). Sao lưu trước khi pull.

---

## 7. Cấu hình

`.env` (mẫu: `.env.example`) và `settings.py`:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `GEMINI_API_KEY` | — | Key Gemini; để trống → dùng Ollama local |
| `GEMINI_CHAT_MODEL` | `gemini-3.1-flash-lite` | Model trả lời chatbot |
| `GEMINI_FALLBACK_MODELS` | `gemini-flash-lite-latest,gemini-3-flash-preview` | Model dự phòng |
| `GEMINI_TIMEOUT` | `30` | Giây chờ mỗi lần gọi |
| `GEMINI_EMBED_MODEL` | `gemini-embedding-001` (đang dùng `gemini-embedding-2`) | Model embedding |
| `GEMINI_EMBED_DIM` | `768` | Số chiều vector |
| `RAG_TOP_K` | `8` | Số đoạn lấy theo nghĩa |
| `RAG_MIN_SCORE` | `0.35` | Ngưỡng điểm tương đồng |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | `900` / `150` | Cắt đoạn khi đồng bộ database / tệp tải lên |

Giới hạn tần suất: `POST /api/chat/` tối đa **15 câu/phút**.

---

## 8. API và giao diện

| Đường dẫn | Mô tả | Quyền |
|---|---|---|
| `/chatbot/` | Trang chatbot toàn màn hình (tài liệu tư vấn, lịch sử, chat) | Ai cũng xem; upload/xóa cần staff |
| (mọi trang) | Khung chat modal `templates/partials/chat_widget.html` | — |
| `/can-bo/hoi-dap/` | Trang cán bộ trả lời câu hỏi chờ | Staff |
| `POST /api/chat/` | Hỏi chatbot `{message, history, client_id}` | — |
| `GET /api/chat/updates/?client_id=` | Lấy câu trả lời cán bộ cho phiên chat | — |
| `/api/chat/sessions/…` | Danh sách / chi tiết / xóa phiên chat | Đăng nhập |
| `/api/tailieu/`, `/api/tailieu/upload/`, `/api/tailieu/<id>/delete/` | Danh sách / tải lên / xóa tài liệu | Upload, xóa: staff |
| `/api/can-bo/cau-hoi/…` | Danh sách / trả lời / xóa câu hỏi chờ | Staff |
| `/api/chatbot/` | API cũ (so từ khóa FAQ) — **legacy**, không dùng cho chatbot chính | — |

---

## 9. Bản đồ file code

| File | Vai trò |
|---|---|
| `admissions/rag.py` | Lõi chatbot: đọc tệp, cắt đoạn, embedding, tìm kiếm (nghĩa + từ khóa), prompt, gọi Gemini, quyết định trả lời / chuyển cán bộ, `add_knowledge` |
| `admissions/knowledge_sync.py` | Đồng bộ database → kho kiến thức; `SYNC_MODELS`, `PORTAL_MODELS`; tín hiệu tự đồng bộ |
| `admissions/apps.py` | Kết nối tín hiệu tự đồng bộ khi khởi động |
| `admissions/views.py` | `api_chat`, `api_chat_updates`, phiên chat, tài liệu, cán bộ; `HANDOFF_REPLY`, `UNAUTH_HANDOFF_REPLY` |
| `admissions/models.py` | `DocumentChunk`, `TaiLieuTuyenSinh`, `CauHoiChoTraLoi`, `ChatSession`, `ChatMessage` |
| `admissions/management/commands/` | `ingest_knowledge_csv`, `sync_knowledge`, `rebuild_embeddings` |
| `templates/partials/chat_widget.html` | Khung chat modal |
| `templates/admissions/chatbot.html` | Trang chatbot toàn màn hình |
| `templates/admissions/officer_qa.html` | Trang cán bộ |
| `CongthongtintuyensinhDUE/settings.py` | Cấu hình Gemini / RAG |

Khi sửa bất kỳ file nào trong bảng trên → **cập nhật tài liệu này**.

---

## 10. Xử lý sự cố thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Câu nào cũng chuyển cán bộ | Kho kiến thức trống (database mới) hoặc thiếu `GEMINI_API_KEY` | Kiểm tra số đoạn trong `admissions_document_chunk`; lấy `db.sqlite3` của nhóm hoặc nạp lại (README); kiểm tra `.env` |
| Dữ liệu có trong database nhưng chatbot không biết | Bảng chưa có trong `SYNC_MODELS` / `PORTAL_MODELS`; dữ liệu nằm trong cột JSON chưa khai báo; hoặc nạp bằng seed/SQL chưa đồng bộ | Làm theo mục 6.1; chạy `sync_knowledge` |
| Chatbot trả lời số liệu cũ | File CSV (ưu tiên 1) có dữ liệu cũ, hoặc còn tệp tải lên cũ | Sửa CSV + `ingest_knowledge_csv`; xóa tệp cũ |
| Trả lời chậm / treo | Model quá tải | Kiểm tra `GEMINI_CHAT_MODEL`, `GEMINI_FALLBACK_MODELS`, `GEMINI_TIMEOUT` |
| Lỗi 429 khi nạp dữ liệu | Hết hạn mức embedding | Chờ hoặc bật thanh toán; xem ai.dev/rate-limit |
| Kết quả tìm kiếm lạ sau khi đổi model embedding | Vector cũ và mới không so được | `rebuild_embeddings` |

---

## 11. Bộ test kiểm tra nhanh

Chạy sau mỗi lần sửa logic chatbot:

| Nhóm | Câu hỏi | Kỳ vọng |
|---|---|---|
| Có trong tài liệu | Học phí Bán phần tiếng Anh 2026? / Mã ngành 7310101 là ngành gì? / Có bao nhiêu liên chi đoàn? | 36,5 triệu / Kinh tế / 8 liên chi đoàn |
| Không có tài liệu | Căng tin có bán cơm chay không? / Wifi trường mật khẩu gì? | Chuyển cán bộ |
| Ngoài phạm vi | có ai bê đê k v / xin chào / giải bài toán 2x+3=7 | Chuyển cán bộ, không tự trả lời |
| Dễ bắt nhầm | k có gì đâu / ngành AI trong kinh doanh học gì? | Chuyển cán bộ / trả lời đúng |
| Nối tiếp | “Học phí bao nhiêu?” → “Còn hệ Toàn phần?” | Hiểu ngữ cảnh: 43 triệu |

Tiêu chí: không câu nào hiển thị dữ liệu thô (“Từ khóa tìm kiếm:”, “Nguồn tham khảo chính thức:”, “Kích hoạt…”) và không có con số ngoài tài liệu.

---

## Lịch sử thay đổi

| Ngày | Thay đổi |
|---|---|
| 05/11/2026 | Chuyển RAG sang Gemini; kho kiến thức 3 nguồn; chuyển câu hỏi cho cán bộ; khung chat modal (PR #9) |
| 06/11/2026 | Đổi tên bảng/URL/lệnh sang tiếng Anh; phiên chat; khách chưa đăng nhập không vào hàng chờ (PR #12) |
| 07/11/2026 | Chặn trả lời bừa: lọc từ phổ biến, bỏ cột Boolean khỏi kiến thức. Chatbot đọc thêm dữ liệu các bảng Khoa, Phòng ban (app `portal`, do Khoa tạo ở PR #12, nạp từ `khoa.json` / `phongban.json`), gồm cả Liên chi đoàn |
| 07/11/2026 | Quy tắc nhóm: mọi câu **không có trong kiến thức** (kể cả ngoài phạm vi, chào hỏi, tán gẫu) đều **chuyển cán bộ**; bỏ câu trả lời cố định `OUT_OF_SCOPE_REPLY` |
