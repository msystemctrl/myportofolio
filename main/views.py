from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from main.forms import ProjectForm
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
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Marsya Rizka Aulia",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "projects.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New project added successfully!")
        return redirect("main:show_projects")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all().order_by('order')

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

GALLERY_POSITIONS = ['g-a', 'g-b', 'g-c', 'g-d', 'g-e', 'g-f']
def show_gallery(request):
    photos = GalleryPhoto.objects.all().order_by('order')[:6]
    gallery_items = list(zip(photos, GALLERY_POSITIONS))
    context = {
        "name": "Marsya Rizka Aulia",
        "gallery_items": gallery_items,
    }
    return render(request, "gallery.html", context)