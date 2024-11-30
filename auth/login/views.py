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
        print("POST so'rov qabul qilindi.")  # Debugging

        try:
            # JSON ma'lumotlarni o'qish
            data = json.loads(request.body)
            login_input = data.get("login_input")
            password = data.get("password")

            if not login_input or not password:
                print("Login yoki parol kiritilmagan.")  # Debugging
                return JsonResponse({"error": "Login yoki parol kiritilishi shart."}, status=400)

            print(f"Kirish uchun kiritilgan ma'lumotlar: input={login_input}, password=****")  # Debugging

            # Login ma'lumotining turini aniqlash
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            phone_regex = r'^998\d{9}$'

            if re.match(email_regex, login_input):
                login_field = 'email'
            elif re.match(phone_regex, login_input):
                login_field = 'phone_number'
            else:
                login_field = 'username'

            print(f"Aniqlangan login maydoni: {login_field}")  # Debugging

            # Foydalanuvchini olish
            if login_field == 'email':
                user = CustomUser.objects.get(email=login_input)
            elif login_field == 'phone_number':
                user = CustomUser.objects.get(phone_number=login_input)
            else:
                user = CustomUser.objects.get(username=login_input)

            # Foydalanuvchini autentifikatsiya qilish
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                print(f"Foydalanuvchi autentifikatsiya qilindi: {user}")  # Debugging

                login(request, user)
                print("Foydalanuvchi sessiyaga kiritildi.")  # Debugging

                # UserActivity log yaratish
                UserActivity.objects.create(
                    user=user,
                    login_time=timezone.now()
                )
                print("UserActivity log yaratildi.")  # Debugging

                return JsonResponse({"message": "Muvaffaqiyatli tizimga kirdingiz."}, status=200)

            else:
                print("Autentifikatsiya muvaffaqiyatsiz.")  # Debugging
                return JsonResponse({"error": "Login yoki parol noto'g'ri."}, status=401)

        except CustomUser.DoesNotExist:
            print("Foydalanuvchi topilmadi.")  # Debugging
            return JsonResponse({"error": "Login yoki parol noto'g'ri."}, status=401)

        except json.JSONDecodeError:
            print("JSON ma'lumotlar noto'g'ri.")  # Debugging
            return JsonResponse({"error": "Noto'g'ri so'rov ma'lumotlari."}, status=400)

        except Exception as e:
            print(f"Xatolik yuz berdi: {str(e)}")  # Debugging
            return JsonResponse({"error": "Ichki xatolik yuz berdi."}, status=500)
