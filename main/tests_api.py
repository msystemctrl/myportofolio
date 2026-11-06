import uuid

from datetime import date

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project, Education, Experience, Songfess


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", meta="Meta test", description="My website", tags="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "meta": "Meta baru", "description": "A useful app",
            "tags": "Python", "order": 2,
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": " "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="Bachelor of Information Systems",
            start_date=date(2025, 1, 1),
            highlights="Poin satu\nPoin dua",
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.payload = {
            "institution": "SMAN Contoh",
            "degree": "SMA",
            "start_date": "2021-07-01",
            "end_date": "2024-06-30",
            "highlights": "Lulus tepat waktu",
        }

    def test_public_can_read_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["institution"], "Universitas Indonesia")
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.client.get(self.list_url, {"institution": "indo"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"institution": "xyz"}).data, [])

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"degree": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.degree, "Bachelor of Information Systems")

    def test_editor_can_patch_and_put_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(self.detail_url, {"degree": "Diubah Editor"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.degree, "Diubah Editor")

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Education.objects.filter(pk=response.data["id"]).exists())

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Education.objects.filter(pk=self.education.id).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution": "<b></b>"}, "institution"),
            ({"degree": " "}, "degree"),
            ({"start_date": "bukan-tanggal"}, "start_date"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 1)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "period_display": "forged", "is_ongoing": True,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["period_display"], "2021 – 2024")
        self.assertFalse(response.data["is_ongoing"])

    def test_missing_education(self):
        url = reverse("api:education-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.other = User.objects.create_user(username="other", password="test-password")
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="teaching",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.appreciate_url = reverse("api:experience-appreciate", args=[self.experience.id])
        self.payload = {
            "title": "Relawan Mengajar",
            "description": "Mengajar anak-anak setiap akhir pekan.",
            "category": "volunteer",
        }

    def test_public_can_read_and_filter_by_category(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Asisten Dosen PBP")
        self.assertEqual(response.data[0]["category_display"], "Teaching")
        self.assertTrue(response.data[0]["is_ongoing"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

        self.assertEqual(len(self.client.get(self.list_url, {"category": "teaching"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"category": "volunteer"}).data, [])

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP")

    def test_editor_can_patch_and_put_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(self.detail_url, {"title": "Diubah Editor"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Diubah Editor")

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"]).exists())

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "<b></b>"}, "title"),
            ({"description": " "}, "description"),
            ({"category": "tidak-ada"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_put_requires_all_required_fields(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"title": "Tidak lengkap"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "started_at": "2000-01-01T00:00:00Z",
            "is_ongoing": False,
            "appreciation_count": 99,
            "is_appreciated": True,
            "appreciated_by_names": "forged",
            "appreciated_by": [self.other.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["started_at"][:4], "2000")
        self.assertTrue(response.data["is_ongoing"])
        self.assertEqual(response.data["appreciation_count"], 0)
        self.assertFalse(response.data["is_appreciated"])

    def test_appreciate_requires_login(self):
        response = self.client.post(self.appreciate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.appreciated_by.count(), 0)

    def test_appreciate_toggles(self):
        self.client.force_authenticate(user=self.visitor)

        response = self.client.post(self.appreciate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_appreciated"])
        self.assertEqual(response.data["appreciation_count"], 1)
        self.assertEqual(response.data["appreciated_by_names"], "visitor")

        response = self.client.post(self.appreciate_url)
        self.assertFalse(response.data["is_appreciated"])
        self.assertEqual(response.data["appreciation_count"], 0)
        self.assertEqual(self.experience.appreciated_by.count(), 0)

    def test_appreciate_uses_request_user_only(self):
        self.client.force_authenticate(user=self.visitor)
        self.client.post(self.appreciate_url, {"user": self.other.id}, format="json")
        self.assertEqual(list(self.experience.appreciated_by.all()), [self.visitor])

    def test_is_appreciated_depends_on_viewer(self):
        self.client.force_authenticate(user=self.visitor)
        self.client.post(self.appreciate_url)

        self.assertTrue(self.client.get(self.detail_url).data["is_appreciated"])

        self.client.force_authenticate(user=self.other)
        response = self.client.get(self.detail_url)
        self.assertFalse(response.data["is_appreciated"])
        self.assertEqual(response.data["appreciation_count"], 1)

    def test_appreciate_get_not_allowed(self):
        self.client.force_authenticate(user=self.visitor)
        response = self.client.get(self.appreciate_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_appreciate_missing_experience(self):
        self.client.force_authenticate(user=self.visitor)
        url = reverse("api:experience-appreciate", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)


class SongfessAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.sender = User.objects.create_user(username="sender", password="test-password")
        self.other = User.objects.create_user(username="other", password="test-password")

        self.pending = Songfess.objects.create(
            requester=self.sender, display_name="Rani", song_title="Lagu Pending",
            song_url="https://open.spotify.com/track/abc123", message="Bikin tenang",
        )
        self.replied = Songfess.objects.create(
            requester=self.other, display_name="Budi", song_title="Lagu Dibalas",
            message="Rahasia pengirim", reply="Terima kasih!",
        )
        self.list_url = reverse("api:songfess-list")
        self.pending_url = reverse("api:songfess-detail", args=[self.pending.id])
        self.replied_url = reverse("api:songfess-detail", args=[self.replied.id])
        self.payload = {
            "display_name": "Dina", "song_title": "Lagu Baru",
            "song_url": "https://youtu.be/dQw4w9WgXcQ", "message": "Semangat",
        }

    # --- Pengunjung ---

    def test_public_list_hides_private_fields(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["song_title"], "Lagu Dibalas")
        self.assertEqual(
            set(response.data[0].keys()),
            {"id", "display_name", "song_title", "song_url", "reply", "created_at"},
        )

    def test_public_detail_hides_unreplied_and_private_fields(self):
        self.assertEqual(self.client.get(self.pending_url).status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.replied_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("message", response.data)
        self.assertNotIn("requester_username", response.data)

    def test_guest_cannot_write(self):
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.patch(self.replied_url, {"song_title": "X"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.replied_url).status_code, 403)
        self.assertEqual(Songfess.objects.count(), 2)
        self.replied.refresh_from_db()
        self.assertEqual(self.replied.song_title, "Lagu Dibalas")

    def test_guest_cannot_use_mine_scope(self):
        response = self.client.get(self.list_url, {"scope": "mine"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Pengguna biasa: kirim dan validasi ---

    def test_user_can_send_song(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["requester_username"], "sender")
        self.assertTrue(response.data["is_mine"])
        self.assertEqual(response.data["reply"], "")
        self.assertEqual(Songfess.objects.count(), 3)

    def test_requester_cannot_be_forged(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post(
            self.list_url, {**self.payload, "requester": self.other.id}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Songfess.objects.get(pk=response.data["id"]).requester, self.sender)

    def test_user_cannot_write_reply(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post(
            self.list_url, {**self.payload, "reply": "balasan palsu"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Songfess.objects.get(pk=response.data["id"]).reply, "")

        response = self.client.patch(self.pending_url, {"reply": "balasan palsu"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.reply, "")

    def test_validation(self):
        self.client.force_authenticate(user=self.sender)
        for changes, field in [
            ({"display_name": "<b></b>"}, "display_name"),
            ({"song_title": " "}, "song_title"),
            ({"song_url": "http://evil.example.com/x"}, "song_url"),
            ({"song_url": "https://evil.example.com/x"}, "song_url"),
            ({"song_url": "javascript:alert(1)"}, "song_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Songfess.objects.count(), 2)

    def test_valid_song_links(self):
        self.client.force_authenticate(user=self.sender)
        for url in [
            "https://open.spotify.com/track/abc123",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        ]:
            response = self.client.post(self.list_url, {**self.payload, "song_url": url}, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, url)

    # --- Pengguna biasa: melihat ---

    def test_user_sees_own_pending_in_mine_scope(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(self.list_url, {"scope": "mine"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [str(self.pending.id)])
        self.assertEqual(response.data[0]["message"], "Bikin tenang")

    def test_user_cannot_see_others_pending(self):
        self.client.force_authenticate(user=self.other)
        self.assertEqual(self.client.get(self.pending_url).status_code, status.HTTP_404_NOT_FOUND)
        ids = [item["id"] for item in self.client.get(self.list_url).data]
        self.assertNotIn(str(self.pending.id), ids)

    # --- Pengguna biasa: ubah dan hapus ---

    def test_user_can_edit_own_before_reply(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.patch(self.pending_url, {"song_title": "Judul Baru"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.song_title, "Judul Baru")

    def test_user_cannot_edit_after_reply(self):
        self.pending.reply = "Sudah dibalas"
        self.pending.save()
        self.client.force_authenticate(user=self.sender)
        response = self.client.patch(self.pending_url, {"song_title": "Judul Baru"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.song_title, "Lagu Pending")

    def test_user_cannot_edit_others_replied(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.patch(self.replied_url, {"song_title": "Dibajak"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.replied.refresh_from_db()
        self.assertEqual(self.replied.song_title, "Lagu Dibalas")

    def test_user_can_delete_own_even_if_replied(self):
        self.pending.reply = "Sudah dibalas"
        self.pending.save()
        self.client.force_authenticate(user=self.sender)
        response = self.client.delete(self.pending_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Songfess.objects.filter(pk=self.pending.id).exists())

    def test_user_cannot_delete_others(self):
        self.client.force_authenticate(user=self.sender)
        self.assertEqual(self.client.delete(self.replied_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Songfess.objects.filter(pk=self.replied.id).exists())

        self.client.force_authenticate(user=self.other)
        self.assertEqual(self.client.delete(self.pending_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Songfess.objects.filter(pk=self.pending.id).exists())

    # --- Pemilik dan Editor ---

    def test_staff_sees_all_with_private_fields(self):
        for user in (self.owner, self.editor):
            self.client.force_authenticate(user=user)
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)
            self.assertTrue(all("message" in item for item in response.data))
            self.assertEqual(self.client.get(self.pending_url).data["message"], "Bikin tenang")

    def test_staff_can_reply(self):
        for user in (self.owner, self.editor):
            self.pending.reply = ""
            self.pending.save()
            self.client.force_authenticate(user=user)
            response = self.client.patch(self.pending_url, {"reply": "Balasan staff"}, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data["is_replied"])
            self.pending.refresh_from_db()
            self.assertEqual(self.pending.reply, "Balasan staff")

    def test_staff_can_delete_any(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.pending_url).status_code, status.HTTP_204_NO_CONTENT)
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.delete(self.replied_url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Songfess.objects.count(), 0)

    def test_reply_length_limit(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.pending_url, {"reply": "x" * 1001}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reply", response.data)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.reply, "")

    def test_search(self):
        self.assertEqual(len(self.client.get(self.list_url, {"search": "dibalas"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"search": "pending"}).data, [])
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(len(self.client.get(self.list_url, {"search": "pending"}).data), 1)

    # --- CSRF ---

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="sender", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Songfess.objects.count(), 2)

    # --- Model dan halaman ---

    def test_songfess_model(self):
        self.assertEqual(str(self.replied), "Lagu Dibalas - Budi")
        self.assertTrue(self.replied.is_replied)
        self.assertFalse(self.pending.is_replied)
        self.pending.reply = "   "
        self.assertFalse(self.pending.is_replied)

    def test_songfess_page_requires_login(self):
        response = self.client.get(reverse("main:show_songfess"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_songfess_page_roles(self):
        self.client.force_login(self.sender)
        response = self.client.get(reverse("main:show_songfess"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "songfess.html")
        self.assertContains(response, "/api/v1/songfess/")
        self.assertContains(response, "My submissions")
        self.assertNotContains(response, 'id="reply-modal"')

        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:show_songfess"))
        self.assertContains(response, "Inbox")
        self.assertContains(response, 'id="reply-modal"')
        self.assertNotContains(response, "My submissions")

    def test_index_shows_login_register_for_guest_only(self):
        songfess_link = f'href="{reverse("main:show_songfess")}"'
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, reverse("main:login"))
        self.assertContains(response, reverse("main:register"))
        self.assertNotContains(response, songfess_link)

        self.client.force_login(self.sender)
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, songfess_link)