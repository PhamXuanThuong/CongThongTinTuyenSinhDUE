from django import forms
from core.sanitization import sanitize_text


class ClubRegistrationForm(forms.Form):
    """Clean and validated submission form for student club registration."""
    ho_ten = forms.CharField(max_length=150, required=True)
    mssv = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    so_dien_thoai = forms.CharField(max_length=20, required=True)
    khoa = forms.CharField(max_length=150, required=False)
    cau_lac_bo_id = forms.CharField(max_length=50, required=True)
    ly_do_tham_gia = forms.CharField(widget=forms.Textarea, required=False)

    def clean_ho_ten(self):
        return sanitize_text(self.cleaned_data.get('ho_ten'))

    def clean_mssv(self):
        return sanitize_text(self.cleaned_data.get('mssv'))

    def clean_so_dien_thoai(self):
        return sanitize_text(self.cleaned_data.get('so_dien_thoai'))

    def clean_ly_do_tham_gia(self):
        return sanitize_text(self.cleaned_data.get('ly_do_tham_gia'))

