from datetime import timedelta
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import MyTokenObtainPairSerializer


def _set_auth_cookies(response: Response, access: str, refresh: str) -> None:
    is_secure = not settings.DEBUG  
    access_max_age = int(
        settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME", timedelta(minutes=25)).total_seconds()
    )
    response.set_cookie(
        key="access_token",
        value=access,
        max_age=access_max_age,
        httponly=True,
        secure=is_secure,
        samesite="Lax",
        path="/",
    )

    refresh_max_age = int(
        settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME", timedelta(days=90)).total_seconds()
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        max_age=refresh_max_age,
        httponly=True,
        secure=is_secure,
        samesite="Lax",
        path="/api/token/refresh/",  
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        request.data["refresh"] = refresh_token

        serializer = self.get_serializer(data=request.data)

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
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/api/token/refresh/")
        return response
