import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Place, Review
from .serializers import UserSerializer, ReviewSerializer


# 🟢 Mekan Listeleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir!)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_list(request):
    places = list(Place.objects.all().values())
    return JsonResponse(places, safe=False, json_dumps_params={'ensure_ascii': False})  


# 🟢 Kullanıcı Kayıt Fonksiyonu
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Kullanıcı başarıyla oluşturuldu!', 'user': serializer.data}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        # 🟢 Kullanıcı oturumunu açık hale getiriyoruz!
        from django.contrib.auth import login
        login(request, user)  # Kullanıcıyı oturum açmış olarak işaretle

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Giriş başarılı!',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=200)
    else:
        return Response({'error': 'Geçersiz kullanıcı adı veya şifre!'}, status=400)


# 🟢 Kullanıcı Yorum Ekleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    user = request.user
    data = request.data

    if Review.objects.filter(user=user, place=place).exists():
        return Response({"error": "Bu mekana zaten yorum yaptınız!"}, status=400)

    review = Review.objects.create(
        user=user,
        place=place,
        comment=data.get('comment'),
        rating=data.get('rating')
    )

    # Ortalama puanı güncelle
    all_reviews = Review.objects.filter(place=place)
    place.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    place.total_reviews = all_reviews.count()
    place.save()

    return Response(ReviewSerializer(review).data, status=201)


# 🟢 Mekana Ait Yorumları Listeleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_reviews(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    reviews = Review.objects.filter(place=place)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=200)
