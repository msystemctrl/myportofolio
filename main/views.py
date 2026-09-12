from django.shortcuts import render

from main.models import Experience, Education, Project, GalleryPhoto


def show_main(request):
    context = {
        "name": "Marsya Rizka Aulia",
        "npm": "2506537606",
        "study_program": "Information Systems",
        "bio": (
            "I am a Computer Science student with a curious mind and a deep "
            "fascination with the stars that illuminate the night sky. Beyond "
            "technology and programming, I find comfort in the distinctive "
            "scent of old books and the stories they carry. One day, I hope "
            "to combine my passion for technology and space by pursuing a "
            "career connected to NASA and contributing to the exploration "
            "of the universe."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Marsya Rizka Aulia",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Marsya Rizka Aulia",
        "education_list": Education.objects.all().order_by('-start_date'),
    }
    return render(request, "education.html", context)

def show_projects(request):
    context = {
        "name": "Marsya Rizka Aulia",
        "project_list": Project.objects.all().order_by('order'),
    }
    return render(request, "projects.html", context)

GALLERY_POSITIONS = ['g-a', 'g-b', 'g-c', 'g-d', 'g-e', 'g-f']
def show_gallery(request):
    photos = GalleryPhoto.objects.all().order_by('order')[:6]
    gallery_items = list(zip(photos, GALLERY_POSITIONS))
    context = {
        "name": "Marsya Rizka Aulia",
        "gallery_items": gallery_items,
    }
    return render(request, "gallery.html", context)