from django.forms import ModelForm, TextInput, Textarea, NumberInput, URLInput

from main.models import Project


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