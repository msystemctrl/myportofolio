from urllib.parse import urlparse

from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project, Education, Experience, Songfess
from main.permissions import is_songfess_staff


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "meta", "description", "tags", "order",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_meta(self, value):
        return strip_tags(value)

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tags(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class EducationSerializer(serializers.ModelSerializer):
    period_display = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    highlight_list = serializers.ReadOnlyField()
    appreciation_count = serializers.SerializerMethodField()
    is_appreciated = serializers.SerializerMethodField()
    appreciated_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            "id", "institution", "degree", "start_date", "end_date",
            "highlights", "period_display", "is_ongoing", "highlight_list",
            "appreciation_count", "is_appreciated", "appreciated_by_names",
        ]
        read_only_fields = ["id"]

    def validate_institution(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Institution cannot be empty.")
        return value

    def validate_degree(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Degree cannot be empty.")
        return value

    def validate_highlights(self, value):
        return strip_tags(value)

    def get_appreciation_count(self, obj):
        return obj.appreciated_by.count()

    def get_is_appreciated(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.appreciated_by.all()

    def get_appreciated_by_names(self, obj):
        return ", ".join(user.username for user in obj.appreciated_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.ReadOnlyField()
    appreciation_count = serializers.SerializerMethodField()
    is_appreciated = serializers.SerializerMethodField()
    appreciated_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "appreciation_count", "is_appreciated", "appreciated_by_names",
        ]
        read_only_fields = ["id", "started_at"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def get_appreciation_count(self, obj):
        return obj.appreciated_by.count()

    def get_is_appreciated(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.appreciated_by.all()

    def get_appreciated_by_names(self, obj):
        return ", ".join(user.username for user in obj.appreciated_by.all())

    
ALLOWED_SONG_HOSTS = {
    "open.spotify.com", "spotify.link",
    "www.youtube.com", "youtube.com", "music.youtube.com", "youtu.be",
}


class SongfessSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source="requester.username", read_only=True)
    is_replied = serializers.ReadOnlyField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Songfess
        fields = [
            "id", "display_name", "message", "song_title", "song_url",
            "reply", "created_at", "is_replied", "requester_username", "is_mine",
        ]
        read_only_fields = ["id", "created_at"]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        # Hanya pemilik dan Editor yang boleh menulis balasan
        if not is_songfess_staff(getattr(request, "user", None)):
            fields["reply"].read_only = True
        return fields

    def validate_display_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Display name cannot be empty.")
        return value

    def validate_message(self, value):
        return strip_tags(value).strip()

    def validate_song_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Song title cannot be empty.")
        return value

    def validate_song_url(self, value):
        if not value:
            return value
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_SONG_HOSTS:
            raise serializers.ValidationError(
                "Song URL must be an https link from Spotify or YouTube."
            )
        return value

    def validate_reply(self, value):
        value = strip_tags(value).strip()
        if len(value) > 1000:
            raise serializers.ValidationError("Reply must be at most 1000 characters.")
        return value

    def get_is_mine(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return obj.requester_id == request.user.id


class PublicSongfessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Songfess
        fields = ["id", "display_name", "song_title", "song_url", "reply", "created_at"]
        read_only_fields = fields