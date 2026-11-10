from django.core.cache import cache
from ninja.errors import HttpError
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .models import User


class IsAuthenticatedCandidate(BasePermission):
    """Allow only authenticated candidate accounts to use protected APIs."""

    message = "A logged-in candidate account is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.CANDIDATE
        )


def candidate_cookie_auth(request):
    """Ninja API auth using the same HttpOnly access cookie as DRF."""
    raw_token = request.COOKIES.get("access_token")
    if not raw_token:
        ip = request.META.get("REMOTE_ADDR", "unknown")
        key = f"api-anon-throttle:{ip}"
        if cache.add(key, 1, timeout=60 * 60):
            return None
        count = cache.incr(key)
        if count > 10:
            raise HttpError(429, "Anonymous request limit exceeded. Try again later.")
        return None

    try:
        token = AccessToken(raw_token)
        user = User.objects.get(pk=token["user_id"], is_active=True)
    except (TokenError, User.DoesNotExist, KeyError, TypeError):
        return None

    if user.role != User.Role.CANDIDATE:
        return None

    key = f"api-user-throttle:{user.pk}"
    if cache.add(key, 1, timeout=60 * 60):
        return user
    if cache.incr(key) > 100:
        raise HttpError(429, "Candidate request limit exceeded. Try again later.")
    return user
