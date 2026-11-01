"""Tải ảnh Liên chi đoàn về máy (chạy trong PyCharm: chuột phải → Run).
Đọc anh_lcd.csv và lưu ảnh vào thư mục images/ cạnh file này."""
import csv, os, urllib.request, time
ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)
ok = fail = 0
with open(os.path.join(ROOT, "anh_lcd.csv"), encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        dest = os.path.join(ROOT, row["file"])
        if os.path.exists(dest):
            ok += 1; continue
        try:
            req = urllib.request.Request(row["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as out:
                out.write(r.read())
            ok += 1; print("OK  ", row["file"])
        except Exception as e:
            fail += 1; print("LỖI ", row["file"], "-", e)
        time.sleep(0.5)
print(f"Xong: {ok} ảnh tải được, {fail} lỗi. Ảnh nằm trong thư mục images/")
