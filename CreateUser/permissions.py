from django.core.cache import cache
from ninja.errors import HttpError
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from .models import User


class IsAuthenticatedCandidate(BasePermission):
    message = "A logged-in candidate account is required."
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.CANDIDATE
        )

class IsAuthenticatedRecruiter(BasePermission):
    message = "A logged-in recruiter account is required."
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.RECRUITER
        )


# Keep the old spelling available for any imports added during development.
IsAuthenticatedRecruitter = IsAuthenticatedRecruiter


class IsVerifiedRecruiter(IsAuthenticatedRecruiter):
    message = "A verified recruiter account is required to post jobs."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        try:
            return request.user.recruiter_profile.is_verified
        except Exception:
            return False


def _check_request_limit(key, limit, message):
    timeout = 60 * 60
    try:
        if cache.add(key, 1, timeout=timeout):
            return

        count = cache.incr(key)
        if count is None:
            # Redis may be unavailable, or the key may expire between add()
            # and incr(). Reinitialize the counter when the backend permits it.
            cache.add(key, 1, timeout=timeout)
            return
    except Exception:
        # CACHES uses django-redis with IGNORE_EXCEPTIONS=True. Keep auth
        # endpoints available if Redis is unavailable; the limiter fails open.
        return

    if count > limit:
        raise HttpError(429, message)


def candidate_cookie_auth(request):
    raw_token = request.COOKIES.get("access_token")
    if not raw_token:
        ip = request.META.get("REMOTE_ADDR", "unknown")
        key = f"api-anon-throttle:{ip}"
        _check_request_limit(
            key,
            10,
            "Anonymous request limit exceeded. Try again later.",
        )
        return None

    try:
        token = AccessToken(raw_token)
        user = User.objects.get(pk=token["user_id"], is_active=True)
    except (TokenError, User.DoesNotExist, KeyError, TypeError):
        return None

    if user.role != User.Role.CANDIDATE:
        return None

    key = f"api-user-throttle:{user.pk}"
    _check_request_limit(
        key,
        100,
        "Candidate request limit exceeded. Try again later.",
    )
    return user
