from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from account.models import Regions, District, Roles, Gender
from school.models import Maktab
from django.shortcuts import redirect
User = get_user_model()  # CustomUser modelini olish


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # JSON ma'lumotlarini o'qish

            print("Kiritilgan ma'lumotlar:", data)

            # Foydalanuvchidan kelgan ma'lumotlarni olish
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone_number_raw = data.get("phone_number")  # Foydalanuvchidan kelgan telefon raqam
            phone_number = phone_number_raw.replace(" ", "").replace("+", "")  # Telefon raqamni formatlash (username uchun)
            email = f"{phone_number}@info.uz"  # Emailni telefon raqamdan hosil qilish
            password = data.get("password")
            region = data.get("region")
            district = data.get("district")
            school_id = data.get("school")

            print(f"Ism: {first_name}, Familiya: {last_name}, Telefon: {phone_number}")
            print(f"Email: {email}, Parol: {password}, Viloyat: {region}, Tuman: {district}, Maktab ID: {school_id}")

            # Parol tasdiqlashni serverda tekshirish
            if not all([first_name, last_name, phone_number_raw, password]):
                print("Xatolik: Barcha maydonlar to'ldirilmagan.")
                return JsonResponse({"error": "Ism, familiya, telefon raqami va parol majburiy."}, status=400)

            # Telefon raqami bo'yicha foydalanuvchini tekshirish
            if User.objects.filter(phone_number=phone_number_raw).exists():
                print(f"Xatolik: Telefon raqami ({phone_number_raw}) allaqachon mavjud.")
                return JsonResponse({"error": "Bu telefon raqami bilan foydalanuvchi allaqachon mavjud."}, status=400)

            # Region, district va maktab obyektlarini olish yoki bo'sh qilib qoldirish
            region_obj = None
            district_obj = None
            school_obj = None

            if region:
                try:
                    region_obj = Regions.objects.get(name=region)
                    print(f"Topilgan region: {region_obj}")
                except Regions.DoesNotExist:
                    print("Viloyat topilmadi. Foydalanuvchi uchun viloyat bo'sh qoldirildi.")

            if district:
                try:
                    district_obj = District.objects.get(name=district)
                    print(f"Topilgan district: {district_obj}")
                except District.DoesNotExist:
                    print("Tuman topilmadi. Foydalanuvchi uchun tuman bo'sh qoldirildi.")

            if school_id:
                try:
                    school_obj = Maktab.objects.get(id=school_id)
                    print(f"Topilgan maktab: {school_obj}")
                except Maktab.DoesNotExist:
                    print("Maktab topilmadi. Foydalanuvchi uchun maktab bo'sh qoldirildi.")

            # Familiya bo'yicha jinsni aniqlash
            gender_obj = None
            if last_name.lower().endswith("va"):
                gender_name = "Ayol"
            else:
                gender_name = "Erkak"

            try:
                gender_obj = Gender.objects.get(name=gender_name)
                print(f"Topilgan jins: {gender_obj}")
            except Gender.DoesNotExist:
                print(f"Jins topilmadi: {gender_name}.")
                return JsonResponse({"error": f"{gender_name} jinsi mavjud emas."}, status=500)

            # Role modeli orqali "O'qituvchi" rolini olish
            try:
                teacher_role = Roles.objects.get(code="2")  # Code "2" is used for "O'qituvchi"
                print(f"Topilgan rol: {teacher_role}")
            except Roles.DoesNotExist:
                return JsonResponse({"error": "O'qituvchi roli mavjud emas."}, status=500)

            # Foydalanuvchini yaratish
            print("Foydalanuvchi yaratilyapti...")
            user = User.objects.create_user(
                username=phone_number,  # Username uchun formatlangan raqam
                email=email,  # Telefon raqamdan hosil qilingan email
                first_name=first_name,
                second_name=last_name,
                phone_number=phone_number_raw,  # Telefon raqami to'liq formatda saqlanadi
                password=password,
                password_save=password,  # Parolni matn holida saqlash
                user_type="2",  # O'qituvchi user_type
                regions=region_obj,  # Region obyektini qo'shish yoki None
                district=district_obj,  # District obyektini qo'shish yoki None
                maktab=school_obj,  # Maktab obyektini qo'shish yoki None
                gender=gender_obj,  # Gender obyektini biriktirish
                now_role="2",  # `now_role`ga avtomatik "O'qituvchi" ni key ni o'rnatish
            )

            # Foydalanuvchiga "O'qituvchi" rolini bog'lash
            user.roles.add(teacher_role)
            user.save()
            print(f"Foydalanuvchi yaratildi va roli bog'landi: {user}")

            # Foydalanuvchini autentifikatsiya qilish
            print("Foydalanuvchini autentifikatsiya qilish...")
            authenticated_user = authenticate(username=phone_number, password=password)

            if authenticated_user:
                print(f"Autentifikatsiya muvaffaqiyatli: {authenticated_user}")
                # Foydalanuvchini tizimga kiritish
                login(request, authenticated_user)
                print("Foydalanuvchi tizimga kiritildi.")
                # Kerakli URL'ga yo'naltirish
                return redirect("main-page-administrator")  # Kerakli URL'ga yo'naltirish
            else:
                print("Xatolik: Autentifikatsiya amalga oshmadi.")
                return JsonResponse({"error": "Autentifikatsiya amalga oshmadi."}, status=400)

        except Exception as e:
            print("Server xatosi:", e)  # Debug uchun log
            return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)

