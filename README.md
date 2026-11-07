# Cổng thông tin Tuyển sinh DUE

Website tuyển sinh Trường Đại học Kinh tế – Đại học Đà Nẵng, xây dựng bằng Django. Có hai tính năng AI dùng Google Gemini:

- **Chatbot tư vấn tuyển sinh**: trả lời dựa trên tài liệu tuyển sinh và dữ liệu website; câu hỏi ngoài tài liệu được chuyển cho cán bộ tuyển sinh trả lời.
- **Tư vấn chọn ngành** (`/huong-nghiep/`): học sinh điền thông tin, AI đề xuất ngành phù hợp tại DUE.

---

## 1. Cài đặt lần đầu

```powershell
# Tại thư mục gốc của repo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Cấu hình AI: copy file mẫu rồi điền GEMINI_API_KEY
copy .env.example .env
```

Lấy key Gemini tại <https://aistudio.google.com/apikey>. Không commit file `.env`.

### Database

`db.sqlite3` **không được lưu trên git** (đã nằm trong `.gitignore`). Có hai cách để có dữ liệu:

1. **Xin file `db.sqlite3` của nhóm** và chép vào `CongthongtintuyensinhDUE/db.sqlite3`
   (đúng thư mục có `manage.py`, không phải thư mục gốc của repo). Cách này nhanh nhất, kho kiến thức chatbot đã có sẵn.
2. **Tự tạo database mới** rồi nạp dữ liệu (tốn khoảng 800 lượt embedding Gemini):

```powershell
cd CongthongtintuyensinhDUE
python manage.py migrate
python manage.py seed_portal_data
python manage.py sync_knowledge
```

> Lưu ý: khi pull code mà file `db.sqlite3` bị xóa khỏi git, database trên máy bạn cũng có thể bị xóa theo. Hãy sao lưu file `db.sqlite3` trước khi pull.

## 2. Chạy dự án

```powershell
cd CongthongtintuyensinhDUE
python manage.py runserver 0.0.0.0:8000
```

- Trên máy: <http://127.0.0.1:8000>
- Máy khác cùng Wi-Fi: `http://<IP-máy-bạn>:8000` (xem IP bằng lệnh `ipconfig`)

---

## 3. Cập nhật kiến thức cho Chatbot

> Tài liệu chi tiết về chatbot (kiến trúc, luồng trả lời, API, file code, xử lý sự cố, bộ test): **[docs/CHATBOT.md](docs/CHATBOT.md)**.
> Sửa logic chatbot thì phải cập nhật tài liệu này (người dùng Claude Code có skill `cap-nhat-tai-lieu-chatbot` hỗ trợ).

Chatbot **không đọc trực tiếp** file Excel/CSV hay database mỗi lần trả lời. Dữ liệu được cắt thành các đoạn nhỏ, chuyển thành vector (embedding) và lưu vào bảng `admissions_document_chunk`. Vì vậy sau khi dữ liệu thay đổi, kho kiến thức phải được cập nhật.

### Trường hợp nào tự động, trường hợp nào phải chạy lệnh

| Bạn thay đổi dữ liệu bằng cách | Chatbot tự cập nhật? | Cần làm gì |
|---|---|---|
| Sửa trong trang **admin** (`/admin/`): ngành, điểm chuẩn, học phí, FAQ, nhập học, tin tức… | ✅ Tự động (khoảng 5 giây) | Không cần làm gì |
| **Tải tài liệu lên** ở trang Chatbot (PDF, DOCX, XLSX, CSV, TXT) bằng tài khoản cán bộ | ✅ Tự động | Thay tài liệu cũ: **xóa file cũ trước** rồi tải bản mới |
| Cán bộ trả lời câu hỏi và tích **“Thêm vào kho kiến thức”** | ✅ Tự động | Không cần làm gì |
| Sửa **trực tiếp database** bằng DB Browser for SQLite hoặc SQL | ❌ Không | Chạy `sync_knowledge` |
| Pull code có migration mới đụng tới dữ liệu kiến thức | ❌ Không | Chạy `migrate` rồi `sync_knowledge` |
| Đổi **model embedding** (`GEMINI_EMBED_MODEL` trong `.env`) | ❌ Không | Chạy `rebuild_embeddings` |

### Các lệnh

Chạy trong thư mục `CongthongtintuyensinhDUE` (thư mục có `manage.py`), đã kích hoạt `.venv`:

```powershell
# Đồng bộ dữ liệu website trong database vào kho kiến thức
# (chỉ tạo embedding cho phần thay đổi nên rất ít tốn lượt)
python manage.py sync_knowledge

# Tạo lại embedding cho toàn bộ kho (khi đổi model embedding, ~800 lượt)
python manage.py rebuild_embeddings
```

### Các bảng đang được tự đồng bộ

Ngành đào tạo, Điểm chuẩn, Phương thức xét tuyển, Loại hình đào tạo, Câu hỏi thường gặp (đang kích hoạt), Học phí, FAQ học phí, Học bổng, Khoa & phòng ban, Chuyên ngành, Hướng dẫn nhập học, Lịch trình tân sinh viên, Tin tức.

Bảng mới muốn chatbot biết (ví dụ Liên chi đoàn, Ký túc xá) cần được thêm vào danh sách `SYNC_MODELS` trong `admissions/knowledge_sync.py`.

### Thứ tự ưu tiên nguồn khi trả lời

1. Tài liệu cán bộ tải lên, câu trả lời của cán bộ
2. Dữ liệu website trong database

Khi hai nguồn mâu thuẫn, chatbot dùng nguồn ưu tiên 1. File `due_knowledge_base_merged.csv` cũ đã bị bỏ, không còn được dùng.

### Nguyên tắc trả lời (không trả lời bừa)

| Tình huống | Chatbot làm gì |
|---|---|
| Có tài liệu (tệp tải lên / database) trả lời **trực tiếp** câu hỏi | Trả lời dựa trên tài liệu, kèm nguồn |
| Không tìm thấy tài liệu liên quan, hoặc AI đánh giá tài liệu không trả lời được câu hỏi | **Chuyển câu hỏi cho cán bộ tuyển sinh** (người chưa đăng nhập: hướng dẫn đăng nhập hoặc gọi hotline) |
| Câu chào hỏi, tán gẫu, câu nhạy cảm, không liên quan tới DUE | **Chuyển cán bộ** (AI không tự trả lời) |
| AI lỗi / hết hạn mức | Chuyển cho cán bộ, không bao giờ hiển thị tài liệu thô |

Các cột kiểu bật/tắt (`BooleanField`, ví dụ `kich_hoat`) không được đưa vào kho kiến thức vì chỉ tạo nhiễu khi tìm kiếm.

---

## 4. Hạn mức Gemini (gói miễn phí)

- Embedding: khoảng **1.000 lượt/ngày** và 100 lượt/phút. Các lệnh nạp dữ liệu tự chia lô và chờ khi bị giới hạn.
- Khi hết lượt embedding, chatbot tự chuyển sang tìm tài liệu theo từ khóa và vẫn trả lời được.
- Xem hạn mức thực tế tại <https://ai.dev/rate-limit>.

## 5. Quy trình làm việc với git

- Không đẩy code thẳng lên `main`. Tạo nhánh riêng (`feature/...`, `fix/...`, `docs/...`) rồi mở Pull Request.
- Không commit `.env` và `db.sqlite3`.
