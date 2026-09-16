from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_education,
    show_projects,
    show_gallery,
    create_project,
    delete_project,
    get_projects_json,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("projects/", show_projects, name="show_projects"),
    path("gallery/", show_gallery, name="show_gallery"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
]