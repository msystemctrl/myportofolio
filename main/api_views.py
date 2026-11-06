from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project, Education, Experience, Songfess
from main.permissions import IsPortfolioOwnerOrReadOnly, IsPortfolioOwnerOrEditorOrReadOnly, IsSongfessSenderOrStaffOrReadOnly, is_songfess_staff
from main.serializers import ProjectSerializer, EducationSerializer, ExperienceSerializer, PublicSongfessSerializer, SongfessSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("order", "title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    if request.method in ("GET", "HEAD"):
        records = Education.objects.prefetch_related("appreciated_by").order_by("-start_date", "id")
        institution = request.query_params.get("institution", "").strip()
        if institution:
            records = records.filter(institution__icontains=institution)
        return Response(EducationSerializer(records, many=True, context={"request": request}).data)

    serializer = EducationSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method in ("GET", "HEAD"):
        return Response(EducationSerializer(education, context={"request": request}).data)

    if request.method == "DELETE":
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = EducationSerializer(
        education, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def education_appreciate(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if education.appreciated_by.filter(pk=request.user.pk).exists():
        education.appreciated_by.remove(request.user)
    else:
        education.appreciated_by.add(request.user)

    serializer = EducationSerializer(education, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ("GET", "HEAD"):
        records = Experience.objects.prefetch_related("appreciated_by").order_by("-started_at", "id")
        category = request.query_params.get("category", "").strip()
        if category:
            records = records.filter(category=category)
        serializer = ExperienceSerializer(
            records, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("appreciated_by"), pk=experience_id,
    )

    if request.method in ("GET", "HEAD"):
        return Response(ExperienceSerializer(experience, context={"request": request}).data)

    if request.method == "DELETE":
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_appreciate(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if experience.appreciated_by.filter(pk=request.user.pk).exists():
        experience.appreciated_by.remove(request.user)
    else:
        experience.appreciated_by.add(request.user)

    serializer = ExperienceSerializer(experience, context={"request": request})
    return Response(serializer.data)


def _visible_songfess(user):
    """Songfess yang boleh dilihat user: staff semua, user login yang
    dibalas atau miliknya, pengunjung hanya yang dibalas"""
    queryset = Songfess.objects.select_related("requester")
    if is_songfess_staff(user):
        return queryset
    if user.is_authenticated:
        return queryset.filter(~Q(reply="") | Q(requester=user))
    return queryset.exclude(reply="")


def _songfess_read_serializer(request, songfess):
    """Staff dan pengirimnya melihat data lengkap, orang lain hanya data publik"""
    context = {"request": request}
    if is_songfess_staff(request.user) or songfess.requester_id == request.user.id:
        return SongfessSerializer(songfess, context=context)
    return PublicSongfessSerializer(songfess, context=context)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsSongfessSenderOrStaffOrReadOnly])
def songfess_list(request):
    if request.method in ("GET", "HEAD"):
        scope = request.query_params.get("scope", "").strip()
        search = request.query_params.get("search", "").strip()

        if scope == "mine":
            if not request.user.is_authenticated:
                raise NotAuthenticated()
            records = Songfess.objects.filter(requester=request.user)
            serializer_class = SongfessSerializer
        elif is_songfess_staff(request.user):
            records = Songfess.objects.all()
            serializer_class = SongfessSerializer
        else:
            records = Songfess.objects.exclude(reply="")
            serializer_class = PublicSongfessSerializer

        if search:
            records = records.filter(
                Q(song_title__icontains=search) | Q(display_name__icontains=search)
            )
        serializer = serializer_class(
            records.select_related("requester"), many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = SongfessSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save(requester=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsSongfessSenderOrStaffOrReadOnly])
def songfess_detail(request, songfess_id):
    songfess = get_object_or_404(_visible_songfess(request.user), pk=songfess_id)

    if request.method in ("GET", "HEAD"):
        return Response(_songfess_read_serializer(request, songfess).data)

    permission = IsSongfessSenderOrStaffOrReadOnly()
    if not permission.has_object_permission(request, None, songfess):
        raise PermissionDenied(permission.message)

    if request.method == "DELETE":
        songfess.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = SongfessSerializer(
        songfess, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)