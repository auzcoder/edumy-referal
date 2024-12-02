import json
import re
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from account.models import UserActivity
from auth.views import AuthView
from django.http import JsonResponse

CustomUser = get_user_model()  # CustomUser modelini olish


class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lsa, ularni asosiy sahifaga yo'naltirish
            return redirect("main-page-administrator")

        # Login sahifasini ko'rsatish
        return super().get(request)

@method_decorator(csrf_exempt, name='dispatch')
class DjangoAuthLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            login_input = data.get("login_input")
            password = data.get("password")

            if not login_input or not password:
                return JsonResponse({"error": "Login yoki parol kiritilishi shart."}, status=400)

            # Identify login type
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            phone_regex = r'^998\d{9}$'

            if re.match(email_regex, login_input):
                login_field = 'email'
            elif re.match(phone_regex, login_input):
                login_field = 'phone_number'
            else:
                login_field = 'username'

            # Get user
            if login_field == 'email':
                user = CustomUser.objects.get(email=login_input)
            elif login_field == 'phone_number':
                user = CustomUser.objects.get(phone_number=login_input)
            else:
                user = CustomUser.objects.get(username=login_input)

            # Authenticate user
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)

                # Log user activity
                UserActivity.objects.create(user=user, login_time=timezone.now())

                # Set session flags for notification
                request.session['last_login'] = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Bu foydalanuvchining birinchi kirishi'
                request.session['show_login_toastr'] = True

                return JsonResponse({"message": "Muvaffaqiyatli tizimga kirdingiz."}, status=200)

            return JsonResponse({"error": "Login yoki parol noto'g'ri."}, status=401)

        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "Login yoki parol noto'g'ri."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Noto'g'ri so'rov ma'lumotlari."}, status=400)

        except Exception as e:
            return JsonResponse({"error": "Ichki xatolik yuz berdi."}, status=500)
