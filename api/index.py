import os
import sys
from pathlib import Path

# Thêm thư mục CongthongtintuyensinhDUE vào sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent / "CongthongtintuyensinhDUE"
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CongthongtintuyensinhDUE.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
