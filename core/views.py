from django.http import JsonResponse
from .models import Place

def place_list(request):
    places = Place.objects.all().values()  # Tüm mekanları veritabanından al
    return JsonResponse(list(places), safe=False)  # JSON olarak döndür
