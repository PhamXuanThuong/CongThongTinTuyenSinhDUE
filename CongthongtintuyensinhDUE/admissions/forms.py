from django import forms
from core.sanitization import sanitize_text


class CounselingRegistrationForm(forms.Form):
    """Clean and validated submission form for admissions counseling."""
    ho_ten = forms.CharField(max_length=150, required=True)
    so_dien_thoai = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    nganh_quan_tam = forms.CharField(max_length=255, required=False)
    noi_dung_cau_hoi = forms.CharField(widget=forms.Textarea, required=False)

    def clean_ho_ten(self):
        return sanitize_text(self.cleaned_data.get('ho_ten'))

    def clean_so_dien_thoai(self):
        return sanitize_text(self.cleaned_data.get('so_dien_thoai'))

    def clean_nganh_quan_tam(self):
        return sanitize_text(self.cleaned_data.get('nganh_quan_tam'))

    def clean_noi_dung_cau_hoi(self):
        return sanitize_text(self.cleaned_data.get('noi_dung_cau_hoi'))


class TuitionCalculationForm(forms.Form):
    """Input validation for tuition fee calculation."""
    slug = forms.CharField(max_length=100, required=False, initial='tieu-chuan')
    year = forms.IntegerField(min_value=0, max_value=3, required=False, initial=0)

    def clean_slug(self):
        val = (self.cleaned_data.get('slug') or 'tieu-chuan').strip().lower()
        slug_map = {
            'tiêu-chuẩn': 'tieu-chuan',
            'tài-năng': 'tai-nang',
            'toàn-phần-ta': 'toan-phan-ta',
            'bán-phần-ta': 'ban-phan-ta',
        }
        return slug_map.get(val, val)

