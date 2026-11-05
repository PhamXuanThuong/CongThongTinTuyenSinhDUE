from typing import List, Dict, Any, Optional
from django.db.models import Q
from tuyensinh.models import (
    LoaiHinhDaoTao,
    PhuongThucXetTuyen,
    NganhDaoTao,
    DiemChuan,
    CauHoiThuongGap,
    TinTuc,
    BangHocPhi,
    CauHoiHocPhi,
)


def get_training_programs():
    """Retrieves all active training program types."""
    return LoaiHinhDaoTao.objects.all().order_by('thu_tu')


def get_admission_methods():
    """Retrieves all active admission methods."""
    return PhuongThucXetTuyen.objects.filter(is_active=True).order_by('thu_tu')


def get_tuition_fees():
    """Retrieves all active tuition fee tiers."""
    return BangHocPhi.objects.filter(is_active=True).order_by('order')


def get_tuition_faqs():
    """Retrieves all active tuition FAQ questions."""
    return CauHoiHocPhi.objects.filter(is_active=True).order_by('order')


def get_faqs():
    """Retrieves general admission FAQs."""
    return CauHoiThuongGap.objects.filter(is_active=True).order_by('thu_tu')


def get_news_articles(limit: int = 5):
    """Retrieves published news articles."""
    return TinTuc.objects.filter(is_published=True).order_by('-ngay_dang')[:limit]


def find_tuition_rate(slug: str):
    """Finds a specific tuition rate by slug."""
    return BangHocPhi.objects.filter(is_active=True).filter(
        Q(slug=slug) | Q(slug='tieu-chuan')
    ).first()

