---
name: cap-nhat-tai-lieu-chatbot
description: Cập nhật tài liệu docs/CHATBOT.md mỗi khi thay đổi logic chatbot. Dùng khi sửa hoặc review thay đổi trong admissions/rag.py, admissions/knowledge_sync.py, các view chat/tài liệu/cán bộ trong admissions/views.py, model DocumentChunk/TaiLieuTuyenSinh/CauHoiChoTraLoi/ChatSession/ChatMessage, lệnh sync_knowledge/rebuild_embeddings, templates chat_widget.html/chatbot.html/officer_qa.html, hoặc cấu hình GEMINI_*/RAG_* trong settings.py và .env.example. Cũng dùng khi người dùng hỏi "chatbot đọc dữ liệu ở đâu", "cập nhật tài liệu chatbot".
---

# Cập nhật tài liệu Chatbot

Tài liệu nguồn sự thật về chatbot là **`docs/CHATBOT.md`**. Mỗi thay đổi logic chatbot phải đi kèm cập nhật tài liệu này **trong cùng commit / PR**.

## Khi nào phải chạy skill này

Bất kỳ thay đổi nào trong các file sau:

| File | Mục cần xem lại trong `docs/CHATBOT.md` |
|---|---|
| `CongthongtintuyensinhDUE/admissions/rag.py` | 3 (luồng), 4 (nguyên tắc), 7 (cấu hình), 10 (sự cố) |
| `CongthongtintuyensinhDUE/admissions/knowledge_sync.py` | 2 (nguồn, danh sách bảng), 6 (cập nhật) |
| `CongthongtintuyensinhDUE/admissions/views.py` (api_chat, api_chat_updates, phiên chat, tài liệu, cán bộ, HANDOFF_REPLY) | 3, 5 (chuyển cán bộ), 8 (API) |
| `CongthongtintuyensinhDUE/admissions/models.py` (DocumentChunk, TaiLieuTuyenSinh, CauHoiChoTraLoi, ChatSession, ChatMessage) | 2, 9 |
| `CongthongtintuyensinhDUE/admissions/urls.py` (đường dẫn chat/tài liệu/cán bộ) | 8 |
| `CongthongtintuyensinhDUE/admissions/management/commands/*` (lệnh kiến thức) | 6 |
| `templates/partials/chat_widget.html`, `templates/admissions/chatbot.html`, `templates/admissions/officer_qa.html` | 8, 9 |
| `settings.py` (GEMINI_*, RAG_*), `.env.example` | 7 |
| **Tạo model mới** (bất kỳ app nào: `admissions/models.py`, `portal/models.py`…) chứa thông tin cho thí sinh | 2, 6.1, 11 — kiểm tra model đã được thêm vào `SYNC_MODELS` / `PORTAL_MODELS` chưa |

## Quy trình

0. **Nếu thay đổi có tạo model / bảng mới** chứa thông tin cho thí sinh: làm theo mục **6.1** của `docs/CHATBOT.md` (thêm vào `SYNC_MODELS` / `PORTAL_MODELS`, khai báo cột JSON, đoạn tổng hợp nếu cần, chạy `sync_knowledge`, hỏi thử). Chạy lệnh kiểm tra bảng chưa đồng bộ trong mục 6.1 và báo cho người dùng nếu còn bảng bị sót. Đây là lỗi đã xảy ra với “Liên chi đoàn”.

1. **Xác định thay đổi**: chạy `git diff` (hoặc `git diff main...HEAD`) trên các file ở bảng trên; ghi rõ hành vi nào thay đổi (nguồn kiến thức, cách tìm kiếm, ngưỡng, prompt, quy tắc chuyển cán bộ, API, lệnh, biến cấu hình).
2. **Đọc lại `docs/CHATBOT.md`** và sửa đúng các mục liên quan. Giữ nguyên cấu trúc 11 mục. Không mô tả điều code không làm.
3. **Đối chiếu số liệu với code thật**, không ghi theo trí nhớ:
   - Giá trị mặc định: `grep -n "RAG_\|GEMINI_" CongthongtintuyensinhDUE/CongthongtintuyensinhDUE/settings.py`
   - Danh sách bảng đồng bộ: `SYNC_MODELS`, `PORTAL_MODELS` trong `knowledge_sync.py`
   - Đường dẫn: `CongthongtintuyensinhDUE/admissions/urls.py`
   - Giới hạn tần suất: `grep -n "rate_limit(" CongthongtintuyensinhDUE/admissions/views.py`
   - Tên lệnh: `ls CongthongtintuyensinhDUE/admissions/management/commands/`
4. **Nếu thay đổi làm kho kiến thức phải tạo lại** (đổi cách chuyển bản ghi thành văn bản, đổi danh sách bảng, đổi model embedding): ghi rõ lệnh cần chạy (`sync_knowledge` / `rebuild_embeddings`) ở mục 6 và trong mô tả PR.
5. **Cập nhật mục 11 (bộ test)** nếu thêm hành vi mới cần kiểm tra; chạy lại bộ test nếu có thể.
6. **Thêm 1 dòng vào “Lịch sử thay đổi”** cuối tài liệu: ngày (dd/mm/yyyy) + tóm tắt thay đổi; sửa dòng “Cập nhật lần cuối” ở đầu file.
7. Nếu thay đổi ảnh hưởng hướng dẫn chung (cài đặt, lệnh), cập nhật thêm mục tương ứng trong `README.md`.
8. Commit tài liệu **cùng** commit/PR với thay đổi code.

## Quy ước nhóm

- Không đẩy thẳng lên `main`; làm trên nhánh riêng rồi mở Pull Request.
- Không commit `.env`, `db.sqlite3`.
- Viết tài liệu bằng tiếng Việt, ngắn gọn, ưu tiên bảng.
