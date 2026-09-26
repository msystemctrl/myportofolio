import datetime

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm         

from main.forms import ProjectForm, EducationForm, ExperienceForm
from main.models import Project, Education, Experience


def show_main(request):
    last_login = request.COOKIES.get('last_login', 
                                     'No previous login session or cookie found.')
    
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
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    json_response = get_experience_json(request)
    experience_list = serializers.deserialize("json", json_response.content.decode("utf-8"))
    experience_list = [item.object for item in experience_list]
    category_query = request.GET.get("category", "").strip()

    context = {
        "name": "Marsya Rizka Aulia",
        "experience_list": experience_list,
        "category_query": category_query,
    }
    return render(request, "experience.html", context)

def get_experience_json(request):
    category_query = request.GET.get("category", "").strip()
    experience_qs = Experience.objects.all().order_by('-started_at')

    if category_query:
        experience_qs =  experience_qs.filter(category=category_query)

    experience_json = serializers.serialize("json", experience_qs, use_natural_foreign_keys=True)
    return HttpResponse(experience_json, content_type="application/json")

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New experience added successfully!")
        return redirect("main:show_experience")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience updated successfully!")
        return redirect("main:show_experience")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


def show_education(request):
    json_response = get_education_json(request)
    education_list = serializers.deserialize("json", json_response.content.decode("utf-8"))
    education_list = [item.object for item in education_list]
    institution_query = request.GET.get("institution", "").strip()

    context = {
        "name": "Marsya Rizka Aulia",
        "education_list": education_list,
        "institution_query": institution_query,
    }
    return render(request, "education.html", context)

def get_education_json(request):
    institution_query = request.GET.get("institution", "").strip()
    education_qs = Education.objects.all().order_by('-start_date')

    if institution_query:
        education_qs = education_qs.filter(institution__icontains=institution_query)

    education_json = serializers.serialize("json", education_qs, use_natural_foreign_keys=True)
    return HttpResponse(education_json, content_type="application/json") # response yang digunakan sebagai API yang menyediakan response/data yang bisa digunakan oleh client

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New education record added successfully!")
        return redirect("main:show_education")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def update_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education record updated successfully!")
        return redirect("main:show_education")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
        "education": education,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education record deleted successfully!")
        return redirect("main:show_education")

    return redirect("main:show_education")


def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize( # mengubah format json menjadi object
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

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all().order_by('order') 

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True) 
    return HttpResponse(projects_json, content_type="application/json")

@login_required(login_url="/login/")
def update_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project record updated successfully!")
        return redirect("main:show_project")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
        "project": project,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")


def show_gallery(request):
    context = {
        'name': 'Marsya Rizka Aulia',
    }

    return render(request, 'gallery.html', context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registration successful. Please log in to continue.")
        return redirect("main:login")

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Marsya Rizka Aulia",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response


@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")