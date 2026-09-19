from django import forms
from django.forms import ModelForm, TextInput, Textarea, NumberInput, URLInput, DateInput, DateTimeInput, Select

from main.models import Project, Education, Experience


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "meta", "description", "tags", "order", "project_url", "project_image_url"]

        labels = {
            "title": "Nama Proyek",
            "meta": "Info Singkat",
            "description": "Deskripsi Proyek",
            "tags": "Tags (pisahkan dengan koma)",
            "order": "Urutan Tampil",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(attrs={"placeholder": "Landing Page Website", "maxlength": 255}),
            "meta": TextInput(attrs={"placeholder": "Perempuan Inovasi 2025 Bootcamp · June 2025", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Ceritakan proyekmu", "rows": 3}),
            "tags": TextInput(attrs={"placeholder": "HTML, CSS, JavaScript"}),
            "order": NumberInput(attrs={"placeholder": "1", "min": 0}),
            "project_url": URLInput(attrs={"placeholder": "https://github.com/username/repo"}),
            "project_image_url": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
        }


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = ["institution", "degree", "start_date", "end_date", "highlights"]

        labels = {
            "institution": "Institusi",
            "degree": "Gelar / Jurusan",
            "start_date": "Tanggal Mulai",
            "end_date": "Tanggal Selesai (kosongkan jika masih berlangsung)",
            "highlights": "Poin Penting (satu poin per baris)",
        }

        widgets = {
            "institution": TextInput(attrs={"placeholder": "Universitas Indonesia", "maxlength": 255}),
            "degree": TextInput(attrs={"placeholder": "Bachelor of Information Systems", "maxlength": 255}),
            "start_date": DateInput(attrs={"type": "date"}),
            "end_date": DateInput(attrs={"type": "date"}),
            "highlights": Textarea(attrs={"placeholder": "Satu poin per baris", "rows": 4}),
        }


class ExperienceForm(ModelForm):
    ended_at = forms.DateTimeField(
        required=False,
        widget=DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="Tanggal Selesai (kosongkan jika masih berlangsung)",
    )

    class Meta:
        model = Experience
        fields = ["title", "description", "category", "thumbnail", "ended_at"]

        labels = {
            "title": "Judul",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "URL Thumbnail (opsional)",
        }

        widgets = {
            "title": TextInput(attrs={"placeholder": "HR Staff, COMPFEST 18", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Ceritakan pengalamanmu", "rows": 4}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
        }