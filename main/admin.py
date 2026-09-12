from django.contrib import admin
from .models import Experience, Education, Project, GalleryPhoto

# Register your models here.
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Project)
admin.site.register(GalleryPhoto)