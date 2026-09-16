import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('organization', 'Organization'),
        ('competition' , 'Competition'),
        ('teaching'    , 'Teaching'),  # Asisten dosen atau tutor
        ('research'    , 'Research'),  # Penelitian atau proyek riset
        ('volunteer'   , 'Volunteer'), # Kegiatan sukarelawan
        ('internship'  , 'Internship'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='organization')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    highlights = models.TextField(help_text="Satu poin per baris")

    def __str__(self):
        return self.institution

    @property
    def is_ongoing(self):
        return self.end_date is None

    @property
    def period_display(self):
        start_year = self.start_date.year
        if self.end_date:
            end_year = self.end_date.year
            return f"{start_year} – {end_year}" if start_year != end_year else f"{start_year}"
        return f"{start_year} – Present"

    @property
    def highlight_list(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    meta = models.CharField(max_length=255, help_text="Contoh: Perempuan Inovasi 2025 Bootcamp · June 2025")
    description = models.TextField()
    tags = models.CharField(max_length=255, help_text="Pisahkan dengan koma, contoh: HTML, CSS, JavaScript")
    order = models.PositiveIntegerField(default=0, help_text="Angka lebih kecil tampil lebih dulu")
    project_url = models.URLField(blank=True)
    project_image_url = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class GalleryPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_path = models.CharField(max_length=255, help_text="Contoh: /static/img/gambar1.jpeg")
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="1-6, menentukan posisi di layout")

    def __str__(self):
        return self.caption or self.image_path