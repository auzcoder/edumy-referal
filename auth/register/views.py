from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

User = get_user_model()  # CustomUser modelini olish


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # JSON ma'lumotlarini o'qish

            # Foydalanuvchidan kelgan ma'lumotlarni olish
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone_number = data.get("phone_number")
            password = data.get("password")
            region = data.get("region")
            district = data.get("district")
            school_id = data.get("school")

            # Parol tasdiqlashni serverda tekshirish
            if not all([first_name, last_name, phone_number, password, region, district]):
                return JsonResponse({"error": "Barcha maydonlarni to'ldirish shart."}, status=400)

            # Telefon raqami bo'yicha foydalanuvchini tekshirish
            if User.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({"error": "Bu telefon raqami bilan foydalanuvchi allaqachon mavjud."}, status=400)

            # Foydalanuvchini yaratish
            user = User.objects.create_user(
                username=phone_number,  # Telefon raqamini username sifatida saqlaymiz
                first_name=first_name,
                second_name=last_name,
                phone_number=phone_number,
                password=password,
                regions_id=region,  # Viloyat ID'si
                district_id=district,  # Tuman ID'si
                maktab_id=school_id,  # Maktab ID'si
            )

            return JsonResponse(
                {"message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tkazildi."},
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)
