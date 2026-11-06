import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from portal.models import Faculty, Department
from admissions.models import CauLacBo


class Command(BaseCommand):
    help = "Seed data from JSON files (khoa.json, phongban.json, clb.json) into database."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Bắt đầu đồng bộ dữ liệu JSON vào Database..."))
        data_dir = os.path.join(settings.BASE_DIR, "data")

        # 1. Seed Faculty (khoa.json)
        khoa_file = os.path.join(data_dir, "khoa.json")
        if os.path.exists(khoa_file):
            with open(khoa_file, "r", encoding="utf-8") as f:
                khoa_list = json.load(f)

            count_faculty = 0
            for idx, item in enumerate(khoa_list):
                fid = item.get("id") or item.get("code")
                if not fid:
                    continue

                Faculty.objects.update_or_create(
                    code=fid,
                    defaults={
                        "name": item.get("name", ""),
                        "faculty_type": item.get("type", "faculty"),
                        "url": item.get("url", ""),
                        "slogan": item.get("slogan", ""),
                        "intro": item.get("intro", ""),
                        "mission": item.get("mission", ""),
                        "vision": item.get("vision", ""),
                        "history": item.get("history"),
                        "staff_summary": item.get("staff_summary", ""),
                        "dean_message": item.get("dean_message", ""),
                        "formed_from": item.get("formed_from") or [],
                        "achievements": item.get("achievements") or [],
                        "career_paths": item.get("career_paths") or [],
                        "notable_activities": item.get("notable_activities") or [],
                        "leadership": item.get("leadership") or {},
                        "departments": item.get("departments") or [],
                        "postgraduate": item.get("postgraduate") or [],
                        "special_programs": item.get("special_programs") or [],
                        "contact": item.get("contact") or {},
                        "links": item.get("links") or {},
                        "major_ids": item.get("major_ids") or [],
                        "majors_2026": item.get("majors_2026") or [],
                        "lien_chi_doan": item.get("lien_chi_doan") or [],
                        "clubs": item.get("clubs") or [],
                        "why_choose": item.get("why_choose") or [],
                        "staff_stats": item.get("staff_stats") or {},
                        "partners": item.get("partners") or [],
                        "student_activities": item.get("student_activities") or [],
                        "clubs_details": item.get("clubs_details") or [],
                        "gallery": item.get("gallery") or [],
                        "aliases": item.get("aliases") or [],
                        "lcd": item.get("lcd") or {},
                        "icon": item.get("icon", "school"),
                        "color": item.get("color", "bg-blue-600"),
                        "border_color": item.get("border_color", ""),
                        "text_color": item.get("text_color", ""),
                        "light_bg": item.get("light_bg", ""),
                        "gradient": item.get("gradient", "from-blue-600 to-indigo-700"),
                        "badge_color": item.get("badge_color", ""),
                        "category_tag": item.get("category_tag", ""),
                        "order": idx,
                        "is_active": True,
                    }
                )
                count_faculty += 1
            self.stdout.write(self.style.SUCCESS(f"-> Đã đồng bộ {count_faculty} Khoa / Viện vào portal_faculty."))
        else:
            self.stdout.write(self.style.WARNING(f"Không tìm thấy file {khoa_file}"))

        # 2. Seed Department (phongban.json)
        pb_file = os.path.join(data_dir, "phongban.json")
        if os.path.exists(pb_file):
            with open(pb_file, "r", encoding="utf-8") as f:
                pb_list = json.load(f)

            count_dept = 0
            for idx, item in enumerate(pb_list):
                pcode = item.get("code")
                if not pcode:
                    continue

                Department.objects.update_or_create(
                    code=pcode,
                    defaults={
                        "name": item.get("name", ""),
                        "short_name": item.get("short_name", ""),
                        "tagline": item.get("tagline", ""),
                        "desc": item.get("desc", ""),
                        "functions": item.get("functions") or [],
                        "duties": item.get("duties") or [],
                        "location": item.get("location", ""),
                        "phone": item.get("phone", ""),
                        "email": item.get("email", ""),
                        "fanpage": item.get("fanpage", ""),
                        "icon": item.get("icon", "domain"),
                        "color": item.get("color", "bg-blue-600"),
                        "badge": item.get("badge", ""),
                        "order": idx,
                        "is_active": True,
                    }
                )
                count_dept += 1
            self.stdout.write(self.style.SUCCESS(f"-> Đã đồng bộ {count_dept} Phòng ban vào portal_department."))
        else:
            self.stdout.write(self.style.WARNING(f"Không tìm thấy file {pb_file}"))

        # 3. Đồng bộ CLB nếu chưa đủ (clb.json -> CauLacBo)
        clb_file = os.path.join(data_dir, "clb.json")
        if os.path.exists(clb_file):
            with open(clb_file, "r", encoding="utf-8") as f:
                clb_list = json.load(f)

            count_clb = 0
            for idx, item in enumerate(clb_list):
                c_slug = item.get("id") or item.get("slug")
                if not c_slug:
                    continue

                CauLacBo.objects.update_or_create(
                    slug=c_slug,
                    defaults={
                        "name": item.get("name", ""),
                        "aliases": item.get("aliases") or [],
                        "level": item.get("level", "Trường (trực thuộc Hội SV)"),
                        "faculty_id": item.get("faculty_id"),
                        "category": item.get("category", "Kỹ năng và khởi nghiệp"),
                        "founded": item.get("founded", ""),
                        "slogan": item.get("slogan", ""),
                        "description": item.get("description", ""),
                        "intro": item.get("intro", ""),
                        "mission": item.get("mission", ""),
                        "vision": item.get("vision", ""),
                        "departments": item.get("departments") or [],
                        "contact": item.get("contact") or {},
                        "leaders": item.get("leaders", ""),
                        "advisors": item.get("advisors", ""),
                        "achievements": item.get("achievements") or [],
                        "recruitment": item.get("recruitment", "Mở đơn định kỳ tháng 8 - tháng 10"),
                        "recruitment_steps": item.get("recruitment_steps") or [],
                        "benefits": item.get("benefits") or [],
                        "followers": item.get("followers", "10K+"),
                        "logo": item.get("logo", ""),
                        "cover": item.get("cover", ""),
                        "gallery": item.get("gallery") or [],
                        "highlights": item.get("highlights") or [],
                        "recent_activities": item.get("recent_activities") or [],
                        "order": idx,
                        "is_active": True,
                    }
                )
                count_clb += 1
            self.stdout.write(self.style.SUCCESS(f"-> Đã đồng bộ {count_clb} Câu lạc bộ vào database."))

        self.stdout.write(self.style.SUCCESS("HOÀN TẤT ĐỒNG BỘ DỮ LIỆU!"))
