import os
import sys
import shutil
from pathlib import Path

# Thêm thư mục CongthongtintuyensinhDUE vào sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent / "CongthongtintuyensinhDUE"
sys.path.insert(0, str(PROJECT_DIR))

# Trên môi trường Vercel (read-only filesystem), copy db.sqlite3 sang /tmp
if "VERCEL" in os.environ:
    db_src = PROJECT_DIR / "db.sqlite3"
    db_dst = Path("/tmp/db.sqlite3")
    try:
        db_dst.parent.mkdir(parents=True, exist_ok=True)
        if db_src.exists() and not db_dst.exists():
            shutil.copy2(db_src, db_dst)
    except Exception as e:
        print(f"Notice Vercel DB copy: {e}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CongthongtintuyensinhDUE.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
