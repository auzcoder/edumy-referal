import re

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from account.models import UserActivity
from auth.views import AuthView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("main-page-administrator")  # Replace 'index' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)


CustomUser = get_user_model()  # CustomUser modelini olish


class JWTAuthView(APIView):
    permission_classes = [AllowAny]  # Kirish vaqtida autentifikatsiya talab qilinmaydi

    def post(self, request):
        print("POST so'rov qabul qilindi.")  # Debugging

        login_input = request.data.get("email")  # Kirish uchun email, username yoki telefon raqam
        password = request.data.get("password")

        print(f"Kirish uchun kiritilgan ma'lumotlar: input={login_input}, password=****")  # Debugging

        # Login ma'lumotining turini aniqlash
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'  # Email formatini tekshirish
        phone_regex = r'^998\d{9}$'  # Telefon raqam formatini tekshirish

        if re.match(email_regex, login_input):
            login_field = 'email'
        elif re.match(phone_regex, login_input):
            login_field = 'phone_number'
        else:
            login_field = 'username'

        print(f"Aniqlangan login maydoni: {login_field}")  # Debugging

        # Autentifikatsiya qilish uchun `username` sifatida mos qiymatni uzatamiz
        user = authenticate(request, username=login_input, password=password)
        if user is not None:
            print(f"Foydalanuvchi autentifikatsiya qilindi: {user}")  # Debugging

            # Django sessiyasi bilan tizimga kirish
            login(request, user)
            print("Foydalanuvchi sessiya tizimiga kiritildi.")  # Debugging

            # UserActivity modelida log yaratish
            UserActivity.objects.create(
                user=user,
                login_time=timezone.now()  # Kirish vaqtini hozirgi vaqt bilan belgilash
            )
            print("UserActivity log yaratildi.")  # Debugging

            # JWT tokenlarni yaratish
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            print(f"JWT tokenlar yaratildi. Access: {access_token}, Refresh: {refresh}")  # Debugging

            # JWT tokenni va sessiya cookie'sini o'rnatish
            response = Response({"message": "Successfully logged in"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=str(access_token),
                httponly=True,
                secure=settings.DEBUG is False,  # Xavfsizlik uchun prodaksiyada True qilib qo'yish
                samesite="Lax",
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            )
            print("Access token cookie'ga o'rnatildi.")  # Debugging

            # Refresh tokenni ham alohida cookie’da saqlash
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            )
            print("Refresh token cookie'ga o'rnatildi.")  # Debugging

            return response
        else:
            print("Autentifikatsiya muvaffaqiyatsiz. Login yoki parol noto'g'ri.")  # Debugging
            return Response({"error": "Login yoki parol noto'g'ri"}, status=status.HTTP_401_UNAUTHORIZED)



class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Cookie'dan access tokenni olish
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None  # Token yo'q bo'lsa, autentifikatsiya qilinmaydi
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed:
            return None  # Token noto'g'ri bo'lsa, autentifikatsiya qilinmaydi
