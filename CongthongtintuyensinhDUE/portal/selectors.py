import os
import json
from typing import List, Dict, Any, Optional
from django.conf import settings

FACULTY_NAMES: Dict[str, str] = {
    'tcnh': 'Khoa Tài chính - Ngân hàng',
    'dlkdqt': 'Khoa Du lịch & Kinh doanh quốc tế',
    'tmdt_mkt_cns': 'Khoa Thương mại điện tử - Marketing và Công nghệ số',
    'kt': 'Khoa Kinh tế',
    'qtkd': 'Khoa Quản trị kinh doanh',
    'ketoan': 'Khoa Kế toán',
    'llct': 'Khoa Lý luận chính trị',
    'luat': 'Khoa Luật',
    'vdtqt': 'Viện Đào tạo Quốc tế',
}


def get_departments() -> List[Dict[str, Any]]:
    """Loads all university administrative and functional departments."""
    pb_path = os.path.join(settings.BASE_DIR, 'data', 'phongban.json')
    if not os.path.exists(pb_path):
        return []
    with open(pb_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_faculties() -> List[Dict[str, Any]]:
    """Loads and formats all faculty and institute records with images and urls."""
    khoa_path = os.path.join(settings.BASE_DIR, 'data', 'khoa.json')
    if not os.path.exists(khoa_path):
        return []

    with open(khoa_path, 'r', encoding='utf-8') as f:
        faculties = json.load(f)
        for fac in faculties:
            fid = fac.get('id')
            fac['logo_url'] = f'/static/img/khoa/{fid}_logo.png'
            fac['cover_url'] = f'/static/img/khoa/{fid}_cover.jpg'
            fac['detail_url'] = f'/khoa/{fid}/'
            fac['lcd_url'] = f'/lien-chi-doan/{fid}/'

            # Format gallery assets
            if 'gallery' in fac and isinstance(fac['gallery'], list):
                for g in fac['gallery']:
                    if isinstance(g, dict) and 'url' in g:
                        if not g['url'].startswith('/'):
                            g['url'] = f'/static/img/khoa/{os.path.basename(g["url"])}'

            # Format LCD data
            if 'lcd' in fac and isinstance(fac['lcd'], dict):
                fac['lcd']['detail_url'] = f'/lien-chi-doan/{fid}/'
                fac['lcd']['faculty_id'] = fid
                fac['lcd']['faculty_name'] = fac.get('name')
                fac['lcd']['color'] = fac.get('color', 'bg-blue-600')
                fac['lcd']['gradient'] = fac.get('gradient', 'from-blue-600 to-indigo-700')
                if 'images' in fac['lcd'] and isinstance(fac['lcd']['images'], list):
                    for img in fac['lcd']['images']:
                        if isinstance(img, dict) and 'url' in img:
                            if not img['url'].startswith('/'):
                                img['url'] = f'/static/img/lcd/{os.path.basename(img["url"])}'
        return faculties


def get_faculty_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Finds a faculty by code or aliases."""
    faculties = get_faculties()
    clean_code = code.strip().rstrip('/').lower()

    for fac in faculties:
        fid = fac.get('id', '').lower()
        aliases = [a.lower() for a in fac.get('aliases', [])]
        if fid == clean_code or clean_code in aliases:
            return fac

    norm_code = clean_code.replace('-', '_')
    for fac in faculties:
        if fac.get('id', '').replace('-', '_') == norm_code:
            return fac

    return None


def get_clubs() -> List[Dict[str, Any]]:
    """Loads clubs from database or fallback to json."""
    try:
        from admissions.models import CauLacBo
        db_clubs = list(CauLacBo.objects.filter(is_active=True).order_by('order', 'id'))
        if db_clubs:
            return [c.to_dict() for c in db_clubs]
    except Exception:
        pass

    clb_path = os.path.join(settings.BASE_DIR, 'data', 'clb.json')
    if os.path.exists(clb_path):
        with open(clb_path, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
            for c in clubs:
                if c.get('logo'):
                    c['logo_url'] = f'/static/img/clb/{os.path.basename(c["logo"])}'
                else:
                    c['logo_url'] = None

                if c.get('cover'):
                    c['cover_url'] = f'/static/img/clb/{os.path.basename(c["cover"])}'
                else:
                    c['cover_url'] = None

                if c.get('gallery'):
                    for g in c['gallery']:
                        if isinstance(g, dict) and 'url' in g:
                            if not g['url'].startswith('/'):
                                g['url'] = f"/static/img/clb/{os.path.basename(g['url'])}"

                fid = c.get('faculty_id')
                c['faculty_name'] = FACULTY_NAMES.get(fid, 'Cấp trường') if fid else 'Cấp trường (Đoàn – Hội)'
            return clubs
    return []


def get_club_by_id(club_id: str) -> Optional[Dict[str, Any]]:
    """Finds club by id or alias."""
    clubs = get_clubs()
    clean_id = club_id.strip().rstrip('/')
    for c in clubs:
        if c.get('id') == clean_id or clean_id in c.get('aliases', []):
            return c
    return None
