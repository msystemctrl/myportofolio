import uuid
from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from main.models import Experience, Education, Project


class ExperienceTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="teaching",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "teaching")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, "/api/v1/experience/")
        self.assertContains(response, "experience-timeline")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

        data = self.client.get(reverse("api:experience-list")).json()
        self.assertEqual(data[0]["title"], self.experience.title)
        self.assertEqual(data[0]["description"], self.experience.description)
        self.assertEqual(data[0]["category_display"], "Teaching")

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experiences have been added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        self.assertFalse(self.experience.is_ongoing)
        data = self.client.get(reverse("api:experience-list")).json()
        self.assertFalse(data[0]["is_ongoing"])


class EducationTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="Bachelor of Information Systems",
            start_date=date(2025, 1, 1),
            highlights="Admitted through SNBP.\nCurrently taking foundational courses.",
        )

    def test_education_model(self):
        self.assertEqual(str(self.education), "Universitas Indonesia")
        self.assertTrue(self.education.is_ongoing)
        self.assertEqual(self.education.period_display, "2025 – Present")
        self.assertEqual(
            self.education.highlight_list,
            ["Admitted through SNBP.", "Currently taking foundational courses."],
        )

    def test_education_page(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, "/api/v1/education/")

        data = self.client.get(reverse("api:education-list")).json()
        self.assertEqual(data[0]["institution"], self.education.institution)
        self.assertEqual(data[0]["degree"], self.education.degree)
        self.assertIn("Admitted through SNBP.", data[0]["highlight_list"])

    def test_completed_education_period_display(self):
        self.education.end_date = date(2029, 1, 1)
        self.education.save()

        self.assertFalse(self.education.is_ongoing)
        self.assertEqual(self.education.period_display, "2025 – 2029")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "No education records have been added yet.")


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Landing Page Website",
            meta="Perempuan Inovasi 2025 Bootcamp",
            description="Built a responsive landing page.",
            tags="HTML, CSS, JavaScript",
            order=1,
        )

    def test_project_model(self):
        self.assertEqual(str(self.project), "Landing Page Website")
        self.assertEqual(self.project.tag_list, ["HTML", "CSS", "JavaScript"])

    def test_projects_page(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertContains(response, "/api/v1/projects/")
        self.assertContains(response, 'id="grid"')

        data = self.client.get(reverse("api:project-list")).json()
        self.assertEqual(data[0]["title"], self.project.title)
        self.assertEqual(data[0]["meta"], self.project.meta)
        self.assertIn("JavaScript", data[0]["tags"])

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "No projects have been added or found.")
        self.assertEqual(self.client.get(reverse("api:project-list")).json(), [])


class EducationAppreciationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.other = User.objects.create_user(username="other", password="test-password")
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="Bachelor of Information Systems",
            start_date=date(2025, 1, 1),
            highlights="Poin satu",
        )
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.appreciate_url = reverse("api:education-appreciate", args=[self.education.id])

    def test_appreciate_requires_login(self):
        response = self.client.post(self.appreciate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.education.appreciated_by.count(), 0)

    def test_appreciate_toggles(self):
        self.client.force_authenticate(user=self.visitor)

        response = self.client.post(self.appreciate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_appreciated"])
        self.assertEqual(response.data["appreciation_count"], 1)
        self.assertEqual(response.data["appreciated_by_names"], "visitor")
        self.assertEqual(self.education.appreciated_by.count(), 1)

        response = self.client.post(self.appreciate_url)
        self.assertFalse(response.data["is_appreciated"])
        self.assertEqual(response.data["appreciation_count"], 0)
        self.assertEqual(self.education.appreciated_by.count(), 0)

    def test_appreciate_uses_request_user_only(self):
        self.client.force_authenticate(user=self.visitor)
        self.client.post(self.appreciate_url, {"user": self.other.id}, format="json")
        self.assertEqual(list(self.education.appreciated_by.all()), [self.visitor])

    def test_is_appreciated_depends_on_viewer(self):
        self.client.force_authenticate(user=self.visitor)
        self.client.post(self.appreciate_url)

        response = self.client.get(self.detail_url)
        self.assertTrue(response.data["is_appreciated"])

        self.client.force_authenticate(user=self.other)
        response = self.client.get(self.detail_url)
        self.assertFalse(response.data["is_appreciated"])
        self.assertEqual(response.data["appreciation_count"], 1)

    def test_appreciation_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {
            "appreciation_count": 99,
            "is_appreciated": True,
            "appreciated_by_names": "forged",
            "appreciated_by": [self.other.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["appreciation_count"], 0)
        self.assertEqual(self.education.appreciated_by.count(), 0)

    def test_appreciate_get_not_allowed(self):
        self.client.force_authenticate(user=self.visitor)
        response = self.client.get(self.appreciate_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_appreciate_missing_education(self):
        self.client.force_authenticate(user=self.visitor)
        url = reverse("api:education-appreciate", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)