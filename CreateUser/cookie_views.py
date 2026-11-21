import os
from datetime import timedelta
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import MyTokenObtainPairSerializer


def _cookie_flags() -> dict:
    is_prod = bool(os.environ.get("RENDER")) or not settings.DEBUG
    return {
        "httponly": True,
        "secure": is_prod,
        "samesite": "None" if is_prod else "Lax",
    }


def _set_auth_cookies(response: Response, access: str, refresh: str) -> None:
    flags = _cookie_flags()

    access_max_age = int(
        settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME", timedelta(minutes=25)).total_seconds()
    )
    response.set_cookie(
        key="access_token",
        value=access,
        max_age=access_max_age,
        path="/",
        **flags,
    )

    refresh_max_age = int(
        settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME", timedelta(days=90)).total_seconds()
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        max_age=refresh_max_age,
        path="/",  # "/" ensures it works both directly and behind the Vercel /backend/ proxy
        **flags,
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        tokens = serializer.validated_data
        access = tokens["access"]
        refresh = tokens["refresh"]
        user_data = tokens.get("user", {})

        response = Response({"user": user_data}, status=status.HTTP_200_OK)
        _set_auth_cookies(response, access, refresh)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = request.data.copy()
        data["refresh"] = refresh_token
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        tokens = serializer.validated_data
        new_access = tokens["access"]
        new_refresh = tokens.get("refresh", refresh_token)

        response = Response({"detail": "Token refreshed."}, status=status.HTTP_200_OK)
        _set_auth_cookies(response, new_access, new_refresh)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        flags = _cookie_flags()
        response.set_cookie("access_token", "", max_age=0, path="/", **flags)
        response.set_cookie("refresh_token", "", max_age=0, path="/", **flags)
        return response