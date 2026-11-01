# Liên chi đoàn các khoa DUE (cập nhật 01/11/2026)

| File | Nội dung |
|---|---|
| `lien_chi_doan.json` | 8 Liên chi đoàn: giới thiệu, nhiệm kỳ, BCH, thành tích, hoạt động có ngày và link bài gốc, danh sách ảnh. Dùng cho code web. |
| `lien_chi_doan.csv` | Mỗi LCĐ một dòng, mở bằng Excel |
| `lien_chi_doan_kien_thuc.md` | Văn bản để nạp cho AI agent |
| `anh_lcd.csv` | các ảnh từ due.udn.vn: link gốc, tên file, chú thích |
| `tai_anh.py` | Script tải toàn bộ ảnh về thư mục `images/` |

## Lấy ảnh

Chạy `tai_anh.py` (trong PyCharm: chuột phải → Run, hoặc gõ `python tai_anh.py`). Ảnh sẽ được lưu vào `images/` với đúng tên file đã ghi trong `lien_chi_doan.json`.

## Còn thiếu

- **Thông tin chưa có:** Bí thư hiện tại của các LCĐ Du lịch – KDQT, TMĐT – Marketing – CNS, Kinh tế, QTKD (trên web chỉ có BCH 2022–2024), Lý luận chính trị và Luật.
- **Ảnh LCĐ Kế toán và Luật:** bài viết của LCĐ Kế toán dùng ảnh Facebook nên link đã hết hạn; bài của LCĐ Luật không có ảnh. Ảnh mới của các LCĐ chủ yếu nằm trên fanpage Facebook.
