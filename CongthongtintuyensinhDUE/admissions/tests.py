"""
Bộ kiểm thử tự động – Cổng thông tin Tuyển sinh DUE (TP3.2 MIS3047)
Chạy:  python manage.py test admissions -v 2 --settings=CongthongtintuyensinhDUE.settings_test

Nhóm A: Xác thực, đăng ký và phân quyền (Thí sinh, Cán bộ tư vấn, Hội đồng tuyển sinh / Admin)
Nhóm B: Kịch bản chính (happy path)
Nhóm C: Cổng XOR / luồng phê duyệt
Nhóm D: Ngoại lệ (dữ liệu sai, lỗi AI, vượt quyền, quá tải)
Nhóm E: Hội đồng tuyển sinh (phê duyệt tài liệu cho AI, báo cáo thống kê, nhắc quá hạn 24 giờ)
Các lời gọi Gemini/Ollama được giả lập (mock) để kiểm thử không phụ thuộc mạng.
"""
import json
from unittest import mock

from django.contrib.auth.models import Group, Permission, User
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from admissions import knowledge_sync
from admissions.models import (
    BangHocPhi, CauHoiChoTraLoi, CauLacBo, DangKyCLB, HoSoHuongNghiep, NganhDaoTao, TaiLieuTuyenSinh,
    ThongBao, TuVanTuyenSinh,
)

AI_RESULT = {
    "tong_quan": "Em thiên về nhóm Quản lý – Nghiên cứu.",
    "majors": [{"ma": "7340115", "ten": "Marketing", "phu_hop": 92, "ly_do": "Hợp nhóm E", "kha_nang": "Cao"}],
    "loi_khuyen": "Đặt Marketing làm nguyện vọng 1.",
}


def _disconnect_kb_signals():
    """Tắt đồng bộ kho kiến thức (gọi API embedding) trong lúc kiểm thử."""
    for name, _ in knowledge_sync.SYNC_MODELS:
        post_save.disconnect(dispatch_uid=f"kb_sync_save_{name}")
        post_delete.disconnect(dispatch_uid=f"kb_sync_delete_{name}")


class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _disconnect_kb_signals()
        cls.admin = User.objects.create_superuser("admin", "a@due.vn", "Admin@123")
        cls.staff = User.objects.create_user("canbo", "c@due.vn", "Canbo@123", is_staff=True)
        grp = Group.objects.create(name="Cán bộ tư vấn tuyển sinh")
        grp.permissions.set(Permission.objects.filter(codename__in=[
            "view_tuvantuyensinh", "change_tuvantuyensinh", "view_cauhoichotraloi", "change_cauhoichotraloi"]))
        cls.staff.groups.add(grp)
        cls.student = User.objects.create_user("thisinh", "t@due.vn", "Thisinh@123")
        cls.hdts = User.objects.create_user("hoidong", "h@due.vn", "Hoidong@123")
        cls.hdts.groups.add(Group.objects.create(name="HDTS"))
        BangHocPhi.objects.create(nhom="Cử nhân chính quy - Tiêu chuẩn", slug="tieu-chuan",
                                  nam_hoc_1=29.5, nam_hoc_2=31.5, nam_hoc_3=33.5, nam_hoc_4=35.5)
        NganhDaoTao.objects.create(ma_nganh="7340115", ten_nganh="Marketing", khoa="Khoa Marketing")
        cls.clb = CauLacBo.objects.create(slug="due-marketer", name="DUE Marketer", description="CLB Marketing")

    def setUp(self):
        cache.clear()
        self.c = Client()

    def chat(self, msg="Học phí bao nhiêu?", client_id="phien_test_0001"):
        return self.c.post("/api/chat/", json.dumps({"message": msg, "client_id": client_id}),
                           content_type="application/json")


# ---------------- A. XÁC THỰC, ĐĂNG KÝ & PHÂN QUYỀN ----------------
class AuthTests(BaseCase):
    def ajax_login(self, u, p):
        return self.c.post("/dang-nhap/", {"username": u, "password": p, "is_ajax": "1"})

    def test_A1_thisinh_login(self):
        r = self.ajax_login("thisinh", "Thisinh@123").json()
        self.assertEqual(r["status"], "success")
        self.assertFalse(r["user"]["is_staff"])

    def test_A2_canbo_login_redirect_officer_workspace(self):
        self.assertEqual(self.ajax_login("canbo", "Canbo@123").json()["redirect_url"], "/chatbot/")

    def test_A3_wrong_password_rejected(self):
        self.assertEqual(self.ajax_login("thisinh", "sai").status_code, 400)

    def test_A4_register_new_account(self):
        r = self.c.post("/dang-ky/", {"last_name": "Nguyễn Nhật", "first_name": "Hạ", "username": "nhatha",
                                      "email": "ha@gmail.com", "password": "Matkhau@1", "confirm_password": "Matkhau@1",
                                      "is_ajax": "1"})
        self.assertEqual(r.json()["status"], "success")
        self.assertFalse(User.objects.get(username="nhatha").is_staff)

    def test_A5_register_duplicate_or_mismatch(self):
        base = {"last_name": "Trần", "first_name": "An", "email": "an@gmail.com", "username": "thisinh",
                "password": "Matkhau@1", "confirm_password": "Matkhau@1", "is_ajax": "1"}
        self.assertEqual(self.c.post("/dang-ky/", base).status_code, 400)
        base.update(username="moi", confirm_password="khac")
        self.assertEqual(self.c.post("/dang-ky/", base).status_code, 400)

    def test_A6_officer_page_requires_staff(self):
        self.assertEqual(self.c.get("/can-bo/hoi-dap/").status_code, 302)
        self.c.force_login(self.student)
        self.assertEqual(self.c.get("/can-bo/hoi-dap/").status_code, 302)
        self.c.force_login(self.staff)
        self.assertEqual(self.c.get("/can-bo/hoi-dap/").status_code, 200)

    def test_A7_canbo_scope_vs_admin(self):
        self.c.force_login(self.staff)
        self.assertEqual(self.c.get("/admin/admissions/cauhoichotraloi/").status_code, 200)
        self.assertEqual(self.c.get("/admin/admissions/diemchuan/").status_code, 403)
        self.c.force_login(self.admin)
        self.assertEqual(self.c.get("/admin/admissions/diemchuan/").status_code, 200)


# ---------------- B. KỊCH BẢN CHÍNH ----------------
class HappyPathTests(BaseCase):
    def test_B1_public_pages_load(self):
        for url in ["/", "/diem-chuan-cac-nam/", "/phuong-thuc-xet-tuyen/", "/hoc-phi/", "/chatbot/",
                    "/huong-nghiep/", "/khoa/", "/clb/", "/huong-dan-nhap-hoc/", "/lich-trinh-tan-sinh-vien/",
                    "/ky-tuc-xa/", "/dang-ky/"]:
            with self.subTest(url=url):
                self.assertEqual(self.c.get(url).status_code, 200)

    def test_B2_tuition_calculator(self):
        r = self.c.get("/api/tinh-hoc-phi/?slug=tieu-chuan&year=0").json()
        self.assertEqual((r["year_vnd"], r["term_vnd"]), (29_500_000, 14_750_000))

    def test_B3_ai_career_advice_saved(self):
        payload = {"full_name": "Nguyễn Nhật Hạ", "phone_number": "0935666777", "email": "ha@gmail.com",
                   "score_r": 2, "score_i": 8, "score_a": 3, "score_s": 4, "score_e": 9, "score_c": 7}
        with mock.patch("admissions.ai_advisor.analyze", return_value=AI_RESULT):
            r = self.c.post("/api/tu-van-huong-nghiep/", json.dumps(payload), content_type="application/json").json()
        self.assertTrue(r["data"]["ai"])
        self.assertEqual(r["data"]["holland_code"], "EIC")
        self.assertIn("[AI]", HoSoHuongNghiep.objects.get().nganh_de_xuat)

    def test_B4_counseling_request_saved(self):
        r = self.c.post("/dang-ky-tu-van/", {"ho_ten": "Lê Minh Châu", "so_dien_thoai": "0905111222"},
                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.json()["status"], "success")
        self.assertEqual(TuVanTuyenSinh.objects.get().trang_thai, "cho_xu_ly")


# ---------------- C. CỔNG XOR / LUỒNG PHÊ DUYỆT ----------------
class GatewayTests(BaseCase):
    def test_C1_chatbot_answers_when_found(self):
        with mock.patch("admissions.rag.answer", return_value=("Học phí 29,5 triệu", ["Đề án 2026"], True)):
            r = self.chat().json()
        self.assertFalse(r["handoff"])
        self.assertEqual(CauHoiChoTraLoi.objects.count(), 0)

    def test_C2_chatbot_handoff_to_officer_when_logged_in(self):
        self.c.force_login(self.student)
        with mock.patch("admissions.rag.answer", return_value=("", [], False)):
            r = self.chat("Thí sinh tự do có được cộng điểm ưu tiên?").json()
        self.assertTrue(r["handoff"])
        self.assertEqual(CauHoiChoTraLoi.objects.get().trang_thai, "cho")

    def test_C3_guest_asked_to_login_instead_of_handoff(self):
        with mock.patch("admissions.rag.answer", return_value=("", [], False)):
            r = self.chat().json()
        self.assertTrue(r["requires_login"])
        self.assertEqual(CauHoiChoTraLoi.objects.count(), 0)

    def test_C4_officer_reply_does_not_write_knowledge(self):
        # To-be: câu trả lời của cán bộ chỉ gửi cho thí sinh; tri thức AI chỉ được bổ sung qua tài liệu đã duyệt.
        q = CauHoiChoTraLoi.objects.create(client_id="phien_test_0001", cau_hoi="KTX có ưu tiên tỉnh xa?")
        self.c.force_login(self.staff)
        with mock.patch("admissions.rag.add_knowledge") as add_kb:
            r = self.c.post(f"/api/can-bo/cau-hoi/{q.id}/tra-loi/",
                            json.dumps({"tra_loi": "Có, ưu tiên hộ khẩu ngoài Đà Nẵng.", "them_kien_thuc": True}),
                            content_type="application/json")
        self.assertEqual(r.status_code, 200)
        add_kb.assert_not_called()
        q.refresh_from_db()
        self.assertEqual((q.trang_thai, q.can_bo), ("da_tra_loi", self.staff))
        upd = Client().get("/api/chat/updates/?client_id=phien_test_0001").json()["data"][0]
        self.assertIn("ưu tiên", upd["tra_loi"])

    def test_C5_counseling_status_flow(self):
        t = TuVanTuyenSinh.objects.create(ho_ten="A", so_dien_thoai="0900000000", noi_dung_cau_hoi="?")
        self.c.force_login(self.staff)
        for action, expected in [("mark_as_in_progress", "dang_tu_van"), ("mark_as_completed", "da_hoan_thanh")]:
            self.c.post("/admin/admissions/tuvantuyensinh/", {"action": action, "_selected_action": [t.pk]})
            t.refresh_from_db()
            self.assertEqual(t.trang_thai, expected)

    def test_C6_club_application_status_flow(self):
        d = DangKyCLB.objects.create(clb=self.clb, ho_ten="B", so_dien_thoai="0911", email="b@x.vn", ly_do_ung_tuyen="x")
        self.assertEqual(d.trang_thai, "cho_duyet")
        d.trang_thai = "trung_tuyen"
        d.save()
        self.assertEqual(DangKyCLB.objects.get().get_trang_thai_display(), "Trúng tuyển")


# ---------------- D. NGOẠI LỆ ----------------
class ExceptionTests(BaseCase):
    def test_D1_ai_error_falls_back_to_officer(self):
        self.c.force_login(self.student)
        with mock.patch("admissions.rag.answer", side_effect=ConnectionError("Gemini timeout")):
            r = self.chat()
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["handoff"])

    def test_D2_career_ai_error_falls_back_to_database(self):
        payload = {"full_name": "A", "phone_number": "0900000000", "score_e": 5}
        with mock.patch("admissions.ai_advisor.analyze", side_effect=RuntimeError("quota")):
            r = self.c.post("/api/tu-van-huong-nghiep/", json.dumps(payload), content_type="application/json").json()
        self.assertFalse(r["data"]["ai"])
        self.assertGreaterEqual(len(r["data"]["suggested_majors"]), 1)

    def test_D3_upload_document_requires_staff(self):
        self.assertEqual(self.c.post("/api/tailieu/upload/").status_code, 403)
        self.c.force_login(self.student)
        self.assertEqual(self.c.post("/api/tailieu/upload/").status_code, 403)

    def test_D4_student_cannot_answer_pending_question(self):
        q = CauHoiChoTraLoi.objects.create(client_id="phien_test_0002", cau_hoi="?")
        self.c.force_login(self.student)
        r = self.c.post(f"/api/can-bo/cau-hoi/{q.id}/tra-loi/", json.dumps({"tra_loi": "x"}),
                        content_type="application/json")
        self.assertEqual(r.status_code, 403)

    def test_D5_officer_empty_reply_rejected(self):
        q = CauHoiChoTraLoi.objects.create(client_id="phien_test_0003", cau_hoi="?")
        self.c.force_login(self.staff)
        r = self.c.post(f"/api/can-bo/cau-hoi/{q.id}/tra-loi/", json.dumps({"tra_loi": " "}),
                        content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_D6_chat_invalid_input(self):
        self.assertEqual(self.c.post("/api/chat/", "not-json", content_type="application/json").status_code, 400)
        self.assertEqual(self.chat(msg="").status_code, 400)
        self.assertEqual(self.chat(client_id="x").status_code, 400)

    def test_D7_chat_rate_limited(self):
        with mock.patch("admissions.rag.answer", return_value=("ok", [], True)):
            codes = [self.chat().status_code for _ in range(16)]
        self.assertEqual(codes[-1], 429)

    def test_D8_career_missing_name_or_wrong_method(self):
        r = self.c.post("/api/tu-van-huong-nghiep/", json.dumps({"phone_number": "09"}), content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.c.get("/api/tu-van-huong-nghiep/").status_code, 405)

    def test_D9_tuition_unknown_year(self):
        self.assertEqual(self.c.get("/api/tinh-hoc-phi/?slug=tieu-chuan&year=9").status_code, 400)


@override_settings(MEDIA_ROOT="/tmp/due_test_media")
class HdtsTests(BaseCase):
    def upload(self, user):
        self.c.force_login(user)
        f = SimpleUploadedFile("de_an_2026.txt", "Đề án tuyển sinh 2026".encode("utf-8"), content_type="text/plain")
        with mock.patch("admissions.rag.index_document", return_value=3) as idx:
            r = self.c.post("/api/tailieu/upload/", {"files": [f]})
        return r, idx

    def test_E1_canbo_upload_waits_for_hdts(self):
        r, idx = self.upload(self.staff)
        self.assertEqual(r.status_code, 200)
        idx.assert_not_called()
        doc = TaiLieuTuyenSinh.objects.get()
        self.assertEqual((doc.status, doc.is_processed, doc.uploaded_by), ("pending", False, self.staff))
        self.assertTrue(ThongBao.objects.filter(nguoi_nhan=self.hdts, loai="upload_moi", tai_lieu=doc).exists())

    def test_E2_hdts_approve_loads_document_into_ai(self):
        self.upload(self.staff)
        doc = TaiLieuTuyenSinh.objects.get()
        self.c.force_login(self.hdts)
        with mock.patch("admissions.rag.index_document", return_value=4) as idx:
            r = self.c.post(f"/api/tailieu/{doc.id}/approve/")
        self.assertEqual(r.json()["chunks_count"], 4)
        idx.assert_called_once()
        doc.refresh_from_db()
        self.assertEqual((doc.status, doc.is_processed, doc.approved_by), ("approved", True, self.hdts))
        self.assertTrue(ThongBao.objects.filter(nguoi_nhan=self.staff, loai="da_duyet").exists())

    def test_E3_hdts_reject_returns_reason_to_canbo(self):
        self.upload(self.staff)
        doc = TaiLieuTuyenSinh.objects.get()
        self.c.force_login(self.hdts)
        r = self.c.post(f"/api/tailieu/{doc.id}/reject/", json.dumps({"reason": "Thiếu quyết định ban hành"}),
                        content_type="application/json")
        self.assertEqual(r.status_code, 200)
        doc.refresh_from_db()
        self.assertEqual((doc.status, doc.is_processed, doc.reject_reason), ("rejected", False, "Thiếu quyết định ban hành"))
        self.assertTrue(ThongBao.objects.filter(nguoi_nhan=self.staff, loai="tu_choi").exists())

    def test_E4_canbo_cannot_approve_or_reject(self):
        self.upload(self.staff)
        doc = TaiLieuTuyenSinh.objects.get()
        self.c.force_login(self.staff)
        self.assertEqual(self.c.post(f"/api/tailieu/{doc.id}/approve/").status_code, 403)
        self.assertEqual(self.c.post(f"/api/tailieu/{doc.id}/reject/").status_code, 403)
        doc.refresh_from_db()
        self.assertEqual(doc.status, "pending")

    def test_E5_statistics_only_for_hdts(self):
        self.c.force_login(self.staff)
        self.assertEqual(self.c.get("/api/hdts/thong-ke/").status_code, 403)
        self.c.force_login(self.hdts)
        r = self.c.get("/api/hdts/thong-ke/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "success")

    def test_E6_question_overdue_after_24h(self):
        q = CauHoiChoTraLoi.objects.create(client_id="phien_test_0002", cau_hoi="Có xét học bạ không?")
        CauHoiChoTraLoi.objects.filter(id=q.id).update(ngay_tao=timezone.now() - timezone.timedelta(hours=25))
        self.c.force_login(self.staff)
        r = self.c.get("/api/can-bo/cau-hoi/").json()
        self.assertEqual(r["overdue_count"], 1)
        self.assertTrue(r["data"][0]["is_overdue"])
