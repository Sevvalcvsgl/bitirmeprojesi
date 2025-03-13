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
from rest_framework.pagination import PageNumberPagination #sayfalama işleminitanımlamak için



# 🟢 Özel Sayfalama Sınıfı (Her sayfada 10 öğe olacak)
class CustomPagination(PageNumberPagination):
    page_size = 10  # Varsayılan olarak her sayfada 5 kayıt göster
    page_size_query_param = 'page_size'  # Kullanıcı isterse ?page_size=20 ile değiştirebilir
    max_page_size = 100  # Maksimum 100 kayıt gösterilebilir

# 🟢 Mekan Listeleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir!)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_list(request):

    places = Place.objects.all()  # QuerySet olarak çağır
    paginator = CustomPagination()  # Sayfalama nesnesi oluştur
    result_page = paginator.paginate_queryset(places, request)  # Sayfalama uygula

    return paginator.get_paginated_response(list(result_page.values()))  # Sayfalı yanıt döndür


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

# 🟢 Kullanıcı Yorum Silme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)  # Yorum bul
    except Review.DoesNotExist:
        return Response({"error": "Yorum bulunamadı!"}, status=404)

    # Yorumun sahibiyle giriş yapmış kullanıcıyı karşılaştırıyoruz
    if review.user != request.user:
        return Response({"error": "Bu yorumu silemezsiniz, çünkü bu sizin yorumunuz değil!"}, status=403)

    review.delete()  # Yorum sil
    return Response({"message": "Yorum başarıyla silindi!"}, status=200)


# 🟢 Kullanıcı Yorum Güncelleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)  # Yorum bul
    except Review.DoesNotExist:
        return Response({"error": "Yorum bulunamadı!"}, status=404)

    # Yorumun sahibiyle giriş yapmış kullanıcıyı karşılaştırıyoruz
    if review.user != request.user:
        return Response({"error": "Bu yorumu güncelleyemezsiniz, çünkü bu sizin yorumunuz değil!"}, status=403)

    # Yorum verisini güncelliyoruz
    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()  # Değişiklikleri kaydet
        return Response({"message": "Yorum başarıyla güncellendi!"}, status=200)
    return Response(serializer.errors, status=400)


# 🟢 Mekana Ait Yorumları Listeleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_reviews(request, place_id):
    place = get_object_or_404(Place, id=place_id)  # Mekanı bul
    reviews = Review.objects.filter(place=place)  # Yorumları çek
    paginator = CustomPagination()  # Sayfalama nesnesi oluştur
    result_page = paginator.paginate_queryset(reviews, request)  # Sayfalama uygula

    serializer = ReviewSerializer(result_page, many=True)  # JSON formatına çevir
    return paginator.get_paginated_response(serializer.data)  # Sayfalı yanıt döndür

