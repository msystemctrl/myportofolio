from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from datetime import date
from main.models import Experience, Education, Project, GalleryPhoto


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
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Teaching")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experiences have been added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


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
        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.degree)
        self.assertContains(response, "Admitted through SNBP.")

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
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.meta)
        self.assertContains(response, "JavaScript")

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "No projects have been added yet.")


class GalleryTest(TestCase):
    def setUp(self):
        self.photo = GalleryPhoto.objects.create(
            image_path="/static/img/gambar1.jpeg",
            caption="Test photo",
            order=1,
        )

    def test_gallery_model(self):
        self.assertEqual(str(self.photo), "Test photo")

    def test_gallery_page(self):
        response = self.client.get(reverse("main:show_gallery"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gallery.html")
        self.assertContains(response, self.photo.image_path)

    def test_empty_gallery_page(self):
        GalleryPhoto.objects.all().delete()
        response = self.client.get(reverse("main:show_gallery"))

        self.assertContains(response, "No photos have been added yet.")

    def test_gallery_caps_at_six_photos(self):
        for i in range(2, 8):
            GalleryPhoto.objects.create(
                image_path=f"/static/img/gambar{i}.jpeg",
                order=i,
            )
        response = self.client.get(reverse("main:show_gallery"))

        self.assertContains(response, "/static/img/gambar6.jpeg")
        self.assertNotContains(response, "/static/img/gambar7.jpeg")