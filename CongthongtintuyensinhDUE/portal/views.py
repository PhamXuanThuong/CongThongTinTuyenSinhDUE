import json
from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest, HttpResponse
from portal import selectors


def faculty_overview_view(request: HttpRequest) -> HttpResponse:
    """Renders the overview of faculties, institutes, and functional departments."""
    faculties = selectors.get_faculties()
    departments = selectors.get_departments()
    return render(request, 'portal/faculties.html', {
        'khoa_list': faculties,
        'phongban_list': departments,
    })


def faculty_detail_view(request: HttpRequest, code: str) -> HttpResponse:
    """Renders details for a specific faculty or institute matching template expectations."""
    faculties = selectors.get_faculties()
    target_faculty = selectors.get_faculty_by_code(code)
    if not target_faculty:
        return redirect('khoa')

    other_faculties = [f for f in faculties if f.get('id') != target_faculty.get('id')]
    phongban_list = selectors.get_departments()
    all_clubs = selectors.get_clubs()
    faculty_clubs = [c for c in all_clubs if c.get('faculty_id') == target_faculty.get('id')]

    return render(request, 'portal/faculty_detail.html', {
        'faculty': target_faculty,
        'other_faculties': other_faculties,
        'all_faculties': faculties,
        'phongban_list': phongban_list,
        'faculty_clubs': faculty_clubs,
    })


def faculty_lcd_detail_view(request: HttpRequest, code: str) -> HttpResponse:
    """Renders youth union (Lien Chi Doan) page for a faculty."""
    faculties = selectors.get_faculties()
    target_faculty = selectors.get_faculty_by_code(code)
    if not target_faculty:
        return redirect('lien_chi_doan_list')

    lcd = target_faculty.get('lcd', {})
    other_faculties = [f for f in faculties if f.get('id') != target_faculty.get('id')]
    all_clubs = selectors.get_clubs()
    faculty_clubs = [c for c in all_clubs if c.get('faculty_id') == target_faculty.get('id')]

    return render(request, 'portal/youth_union_detail.html', {
        'faculty': target_faculty,
        'lcd': lcd,
        'faculty_clubs': faculty_clubs,
        'other_faculties': other_faculties,
        'all_faculties': faculties,
    })


def lcd_overview_view(request: HttpRequest) -> HttpResponse:
    """Renders overview list of all youth union branches."""
    faculties = selectors.get_faculties()
    all_clubs = selectors.get_clubs()

    for fac in faculties:
        fid = fac.get('id')
        fac_clubs = [c for c in all_clubs if c.get('faculty_id') == fid]
        fac['clubs_count'] = len(fac_clubs)
        fac['faculty_clubs'] = fac_clubs

    return render(request, 'portal/youth_unions.html', {
        'faculties': faculties,
        'faculty_count': len(faculties),
        'clubs_count': len(all_clubs),
    })


def club_view(request: HttpRequest) -> HttpResponse:
    """Renders student clubs list."""
    clubs = selectors.get_clubs()
    clubs_json = json.dumps(clubs, ensure_ascii=False)
    return render(request, 'portal/clubs.html', {
        'clubs': clubs,
        'clubs_json': clubs_json,
        'clubs_count': len(clubs),
    })


def club_detail_view(request: HttpRequest, club_id: str) -> HttpResponse:
    """Renders detail information for a single club."""
    clubs = selectors.get_clubs()
    club = selectors.get_club_by_id(club_id)
    if not club:
        return redirect('clb')

    related = [
        c for c in clubs
        if c.get('id') != club.get('id') and (
            c.get('category') == club.get('category') or
            (c.get('faculty_id') and c.get('faculty_id') == club.get('faculty_id')) or
            c.get('level') == club.get('level')
        )
    ]
    if len(related) < 4:
        others = [c for c in clubs if c.get('id') != club.get('id') and c not in related]
        related.extend(others[:4 - len(related)])
    else:
        related = related[:4]

    return render(request, 'portal/club_detail.html', {
        'club': club,
        'related_clubs': related,
        'all_clubs': clubs,
    })


def dormitory_view(request: HttpRequest) -> HttpResponse:
    """Renders dormitory & student housing guide."""
    return render(request, 'portal/dormitory.html')


def youth_activity_view(request: HttpRequest) -> HttpResponse:
    """Renders youth union general activities."""
    return render(request, 'portal/youth_activities.html')


def student_life_view(request: HttpRequest) -> HttpResponse:
    """Renders student life and extracurricular portal."""
    return club_view(request)


def enrollment_guide_view(request: HttpRequest) -> HttpResponse:
    """Renders formal enrollment guide for new students."""
    return render(request, 'portal/enrollment_guide.html')


def freshman_schedule_view(request: HttpRequest) -> HttpResponse:
    """Renders freshman welcome orientation schedule."""
    return render(request, 'portal/freshman_schedule.html')
