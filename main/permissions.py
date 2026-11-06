from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )
    

class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )


def is_songfess_staff(user):
    return bool(
        user is not None
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="Editor").exists())
    )


class IsSongfessSenderOrStaffOrReadOnly(BasePermission):
    message = "You can only change your own songfess, and only before it has been replied."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if is_songfess_staff(request.user):
            return True
        if obj.requester_id != request.user.id:
            return False
        return request.method == "DELETE" or not obj.is_replied