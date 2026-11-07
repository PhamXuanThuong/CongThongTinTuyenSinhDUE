import os
import sys
import shutil
from pathlib import Path

# Thêm thư mục CongthongtintuyensinhDUE vào sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent / "CongthongtintuyensinhDUE"
sys.path.insert(0, str(PROJECT_DIR))

# Trên môi trường Vercel:
# 1. Nếu có cấu hình Turso DB, tự động đồng bộ dữ liệu thật mới nhất từ Turso về /tmp/db.sqlite3
# 2. Nếu không có Turso, fallback copy file db.sqlite3 cục bộ
if "VERCEL" in os.environ:
    db_dst = Path("/tmp/db.sqlite3")
    turso_url = os.environ.get("TURSO_DATABASE_URL", "").strip()
    turso_token = os.environ.get("TURSO_AUTH_TOKEN", "").strip()

    synced_from_turso = False
    if turso_url and turso_token and not db_dst.exists():
        try:
            import requests
            import sqlite3

            dump_url = turso_url
            if dump_url.startswith("libsql://"):
                dump_url = "https://" + dump_url[len("libsql://") :]
            dump_url = dump_url.rstrip("/") + "/dump"

            resp = requests.get(
                dump_url,
                headers={"Authorization": f"Bearer {turso_token}"},
                timeout=15,
            )
            if resp.status_code == 200 and resp.text:
                db_dst.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(db_dst))
                conn.executescript(resp.text)
                conn.close()
                synced_from_turso = True
                print("Successfully hydrated SQLite from Turso cloud database!")
        except Exception as err:
            print(f"Warning: Turso sync failed ({err}), falling back to local file.")

    if not synced_from_turso and not db_dst.exists():
        db_src = PROJECT_DIR / "db.sqlite3"
        try:
            db_dst.parent.mkdir(parents=True, exist_ok=True)
            if db_src.exists():
                shutil.copy2(db_src, db_dst)
        except Exception as e:
            print(f"Notice Vercel DB copy: {e}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CongthongtintuyensinhDUE.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
