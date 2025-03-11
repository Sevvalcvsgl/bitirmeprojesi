import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes  # 🟢 permission_classes eklendi!
from rest_framework.permissions import IsAuthenticated  # 🟢 Yetkilendirme için import edildi!
from .models import Place
from .serializers import UserSerializer  
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# 🟢 Mekan Listeleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir!)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 🟢 Sadece giriş yapan kullanıcılar erişebilir!
def place_list(request):
    places = list(Place.objects.all().values())
    return JsonResponse(places, safe=False, json_dumps_params={'ensure_ascii': False})  # 🟢 UTF-8 desteği

# Kullanıcı Kayıt Fonksiyonu
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Kullanıcı başarıyla oluşturuldu!', 'user': serializer.data}, status=201)
    return Response(serializer.errors, status=400)

# Kullanıcı Giriş Fonksiyonu (JWT ile)
@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Giriş başarılı!',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=200)
    else:
        return Response({'error': 'Geçersiz kullanıcı adı veya şifre!'}, status=400)
