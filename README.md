# Cổng Thông Tin Tuyển Sinh DUE

Hệ thống thông tin tuyển sinh tích hợp trợ lý số thông minh dựa trên kiến trúc RAG (Retrieval-Augmented Generation) và mô hình định hướng nghề nghiệp Holland, phục vụ công tác tuyển sinh tại Trường Đại học Kinh tế – Đại học Đà Nẵng (DUE).

---

## 1. Tổng quan hệ thống

Dự án được xây dựng nhằm chuẩn hóa, số hóa và tự động hóa toàn diện quy trình cung cấp thông tin tuyển sinh, giải đáp thắc mắc và định hướng ngành học cho thí sinh. Hệ thống tích hợp các phân hệ nghiệp vụ chính:

- **Cổng thông tin tuyển sinh công khai:** Cung cấp thông tin chính thống về đề án tuyển sinh, chỉ tiêu, tổ hợp xét tuyển, điểm chuẩn nhiều năm, chính sách học phí - học bổng, cũng như hệ thống thông tin các Khoa, Viện và Câu lạc bộ.
- **Trợ lý số giải đáp tuyển sinh (RAG-based AI Chatbot):** Tự động truy xuất thông tin chính xác từ cơ sở dữ liệu website và tài liệu số đã qua thẩm định để tạo sinh câu trả lời tự nhiên, chính xác, có trích dẫn nguồn cụ thể. Hỗ trợ cơ chế định tuyến câu hỏi (handoff) sang cán bộ tuyển sinh khi câu hỏi vượt quá phạm vi dữ liệu tự động.
- **Hệ thống tư vấn chọn ngành & Định hướng nghề nghiệp:** Kết hợp lý thuyết mật mã nghề nghiệp RIASEC (John Holland) với mô hình phân tích ngữ nghĩa của mô hình ngôn ngữ lớn (LLM), giúp lượng hóa sở thích, năng lực cá nhân để gợi ý ngành học phù hợp tại DUE.
- **Phân hệ Thẩm định & Quản trị dữ liệu (Dành cho Cán bộ & Hội đồng Tuyển sinh):** Quản lý quy trình vòng đời của tài liệu (tải lên $\rightarrow$ thẩm định $\rightarrow$ phê duyệt $\rightarrow$ vector hóa dữ liệu), giám sát báo cáo thống kê lượt hỏi, khung giờ cao điểm và phân loại các chủ đề tuyển sinh trọng điểm.

---

## 2. Kiến trúc công nghệ

Hệ thống được phát triển theo mô hình kiến trúc phân lớp (Layered Architecture):

- **Backend Framework:** Python 3.10+ / Django 5.x / Django REST Framework.
- **Database:** SQLite (Môi trường nghiên cứu & phát triển) / PostgreSQL (Sẵn sàng triển khai sản xuất).
- **Trí tuệ nhân tạo (Generative AI & Semantic Retrieval):**
  - **Large Language Models (LLM):** Google Gemini Models (`gemini-2.5-flash` / `gemini-1.5-flash`), hỗ trợ tích hợp Ollama cục bộ.
  - **Vector Embedding & RAG:** Mô hình `text-embedding-004`, tính toán độ tương đồng Cosine kết hợp thuật toán tìm kiếm từ khóa nâng cao (Hybrid Search: Dense Vector + Sparse BM25-like).
  - **Semantic Vector Storage:** Bảng lưu trữ vector nhúng nội bộ `admissions_document_chunk` với cơ chế phân đoạn (chunking), đánh chỉ mục và tính độ tương đồng theo thời gian thực.
- **Frontend Architecture:** Django Templates, Tailwind CSS, Material Symbols, Vanilla JavaScript (ES6+ Asynchronous AJAX, Fetch API).
- **Bảo mật & Kiểm soát truy cập:** Role-Based Access Control (RBAC) với các nhóm đối tượng: Khách vãng lai / Thí sinh, Cán bộ tuyển sinh (`is_staff`), Hội đồng Tuyển sinh (`HDTS`).

---

## 3. Kiến trúc luồng xử lý RAG & Phân cấp tri thức

Nhằm đảm bảo tính chính xác và tránh hiện tượng ảo giác (hallucination) của mô hình ngôn ngữ, hệ thống triển khai cơ chế ưu tiên dữ liệu đa tầng:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 Dữ liệu đầu vào                         │
                  └──────────┬───────────────────────────────┬─────────────┘
                             │                               │
              [Ưu tiên 1: Thẩm định HĐTS]        [Ưu tiên 2: Dữ liệu Website]
              - Văn bản số (PDF, DOCX, TXT)      - Đề án, Điểm chuẩn, Học phí
              - Cặp hỏi đáp từ Cán bộ            - Dữ liệu Khoa, Viện, Ngành
                             │                               │
                             └───────────────┬───────────────┘
                                             ▼
                             ┌───────────────────────────────┐
                             │       Chunking & Embedding    │
                             │ (Bảng admissions_doc_chunk)   │
                             └───────────────┬───────────────┘
                                             ▼
              [Người dùng gửi câu hỏi] ──► Hybrid Retrieval (Vector + Từ khóa)
                                             │
                                             ▼
                                     Trích xuất Top-K
                                (Rọc bỏ nguồn mâu thuẫn)
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     LLM Gemini Prompt     │
                               │  (Chỉ trả lời theo bối cảnh)│
                               └─────────────┬─────────────┘
                                             │
                    ┌────────────────────────┴────────────────────────┐
                    ▼                                                 ▼
            [Đủ dữ liệu]                                    [Không đủ dữ liệu]
      Trả lời kèm trích dẫn nguồn                    Chuyển phiên cho Cán bộ tiếp nhận
```

1. **Phân đoạn và nhúng vector:** Dữ liệu từ database và tài liệu thẩm định được chuẩn hóa, loại bỏ siêu dữ liệu thừa và phân tách thành các đoạn văn bản (chunks) theo ngưỡng cấu hình (`RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`).
2. **Xử lý tín hiệu song song:** Khi nhận truy vấn, hệ thống đồng thời tạo vector nhúng để tìm kiếm theo độ tương đồng ngữ nghĩa và trích xuất từ khóa đặc thù (mã ngành, tổ hợp xét tuyển, chỉ tiêu).
3. **Ưu tiên nguồn văn bản:** Các tài liệu do Hội đồng Tuyển sinh thẩm định và phê duyệt (Ưu tiên 1) có trọng số cao nhất; khi có mâu thuẫn số liệu, nguồn dữ liệu này sẽ ghi đè lên các dữ liệu website thông thường.

---

## 4. Hướng dẫn cài đặt và thiết lập môi trường

### 4.1. Yêu cầu tiên quyết

- Python 3.10 trở lên.
- Trình quản lý gói `pip` và công cụ tạo môi trường ảo `venv`.

### 4.2. Khởi tạo môi trường ảo và cài đặt thư viện

```powershell
# Di chuyển vào thư mục gốc của dự án
cd "CongThongTinTuyenSinhDUE"

# Tạo và kích hoạt môi trường ảo
python -m venv .venv
.venv\Scripts\activate

# Cài đặt danh mục các gói phụ thuộc
pip install -r requirements.txt
```

### 4.3. Khởi tạo cơ sở dữ liệu và đồng bộ kho tri thức

```powershell
cd CongthongtintuyensinhDUE

# Thực thi migration định nghĩa schema cơ sở dữ liệu
python manage.py migrate

# Đồng bộ hóa và tạo vector nhúng tri thức vào database
python manage.py sync_knowledge
```

---

## 5. Vận hành hệ thống

Khởi chạy máy chủ phát triển cục bộ:

```powershell
python manage.py runserver
```

Hệ thống truy cập qua các địa chỉ:

- **Trang chủ Cổng thông tin Tuyển sinh:** `http://127.0.0.1:8000/`
- **Trợ lý tư vấn AI Chatbot:** `http://127.0.0.1:8000/chatbot/`
- **Hệ thống tư vấn hướng nghiệp & trắc nghiệm:** `http://127.0.0.1:8000/huong-nghiep/`
- **Bảng điều khiển Thống kê Hội đồng Tuyển sinh:** `http://127.0.0.1:8000/hdts/thong-ke/`
- **Khu vực Cán bộ giải đáp câu hỏi:** `http://127.0.0.1:8000/can-bo/tra-loi/`
- **Trang quản trị Django:** `http://127.0.0.1:8000/admin/`

---

## 6. Lệnh quản trị nghiệp vụ (Management Commands)

Các tác vụ hậu trường được đóng gói thành các câu lệnh Django Management:

| Lệnh thực thi                         | Mục đích sử dụng                                                                                                                     |
| :------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| `python manage.py sync_knowledge`     | Quét các thay đổi trong cơ sở dữ liệu website, tạo vector nhúng bổ sung vào kho tri thức RAG (hỗ trợ phân lô để tối ưu hạn mức API). |
| `python manage.py rebuild_embeddings` | Xóa và tái tạo toàn bộ vector nhúng trong kho tri thức khi có sự thay đổi về mô hình embedding.                                      |
| `python manage.py seed_portal_data`   | Khởi tạo cấu trúc danh mục ban đầu cho các đơn vị Khoa, Viện, Ngành học và Câu lạc bộ trực thuộc.                                    |

---

## 7. Cấu trúc thư mục dự án

```text
CongThongTinTuyenSinhDUE/
├── CongthongtintuyensinhDUE/        # Thư mục gốc chứa mã nguồn Django
│   ├── admissions/                 # Nghiệp vụ tuyển sinh, RAG & Chatbot
│   │   ├── admin.py                # Cấu hình giao diện quản trị Django Admin
│   │   ├── models.py               # Định nghĩa ORM Models (Tài liệu, Ngành, Q&A, Chat)
│   │   ├── rag.py                  # Module xử lý thuật toán RAG, Vector Search & LLM
│   │   ├── knowledge_sync.py       # Cơ chế đồng bộ dữ liệu quan hệ sang dữ liệu vector
│   │   ├── ai_advisor.py           # Module AI xử lý gợi ý ngành học Holland
│   │   ├── views.py                # Controller xử lý luồng HTTP và REST API
│   │   └── urls.py                 # Định tuyến đường dẫn nội bộ
│   ├── portal/                     # Thông tin sinh viên, Khoa, Viện, CLB
│   ├── core/                       # Các tiện ích dùng chung: Sanitize, Rate-limit
│   ├── templates/                  # Hệ thống giao diện Django Templates
│   │   ├── admissions/             # Template Chatbot, Hướng nghiệp, Thống kê HĐTS
│   │   ├── auth/                   # Giao diện Đăng ký, Đăng nhập
│   │   ├── layouts/                # Base layout, Header, Footer, Popup chung
│   │   └── partials/               # Widget chat AI nổi, linh kiện giao diện phụ trợ
│   ├── static/                     # Tệp tĩnh: CSS, JavaScript, Media, Favicon
│   └── manage.py                   # Điểm thực thi quản trị dự án
├── requirements.txt                # Danh mục các thư viện và phụ thuộc
├── .env.example                    # Tệp mẫu cấu hình môi trường
└── README.md                       # Tài liệu tổng quan dự án
```
