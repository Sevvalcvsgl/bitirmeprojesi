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
from .models import Place, FavoritePlace  # FavoritePlace modelini ekledik!



# 🟢 Özel Sayfalama Sınıfı (Her sayfada 10 öğe olacak)
class CustomPagination(PageNumberPagination):
    page_size = 10  # Varsayılan olarak her sayfada 5 kayıt göster
    page_size_query_param = 'page_size'  # Kullanıcı isterse ?page_size=20 ile değiştirebilir
    max_page_size = 100  # Maksimum 100 kayıt gösterilebilir

# 🟢 Mekan Listeleme Fonksiyonu (Sadece giriş yapmış kullanıcılar erişebilir!)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_list(request):
    
      category_filter = request.GET.get('category')  # 🟡 Kategori parametresi
    min_rating = request.GET.get('min_rating')  # 🟡 Minimum puan filtresi
    search_query = request.GET.get('search')  # 🟡 Mekan adıyla arama
    location_filter = request.GET.get('location')  # 🟡 Konum filtresi
    sort_by = request.GET.get('sort_by', '-rating')  # 🟡 Varsayılan olarak puana göre azalan sıralama
    price_filter = request.GET.get('price')
    wifi_filter = request.GET.get('wifi')


    places = Place.objects.all()

    # 🟡 Kategori filtresi (birden fazla kategori seçilebilir: ?category=study,romantic)
    if category_filter:
        categories = category_filter.split(',')  # Virgülle ayrılmış kategorileri liste yap
        places = places.filter(category__in=categories)

    # 🟡 Minimum puan filtresi (Örn: ?min_rating=4)
    if min_rating:
        try:
            min_rating = float(min_rating)
            places = places.filter(rating__gte=min_rating)
        except ValueError:
            return Response({"error": "Geçersiz min_rating değeri!"}, status=400)

    # 🟡 Mekan adıyla arama (Örn: ?search=Starbucks)
    if search_query:
        places = places.filter(name__icontains=search_query)

    # 🟡 Konum filtresi (Örn: ?location=İstanbul)
    if location_filter:
        places = places.filter(location__icontains=location_filter)

    # 🟡 Fiyat filtresi (Örn: ?price=low,medium,high)
    if price_filter:
        price_levels = price_filter.split(',')
        places = places.filter(price__in=price_levels)

    # 🟡 Wi-Fi filtresi (Örn: ?wifi=true veya ?wifi=false)
    if wifi_filter is not None:
        if wifi_filter.lower() == "true":
            places = places.filter(has_wifi=True)
        elif wifi_filter.lower() == "false":
            places = places.filter(has_wifi=False)

    # 🟡 Sıralama filtresi (Örn: ?sort_by=total_reviews) 
    valid_sort_fields = ['name', '-name', 'rating', '-rating', 'total_reviews', '-total_reviews']
    if sort_by in valid_sort_fields:
        places = places.order_by(sort_by)
    else:
        places = places.order_by('-rating')  # Varsayılan olarak puana göre sıralama


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
    review = get_object_or_404(Review, id=review_id)  # 🟡 Yorum bul (get yerine get_object_or_404 kullanıldı)

    # 🟡 Kullanıcının kendi yorumunu güncellemesini sağlıyoruz
    if review.user != request.user:
        return Response({"error": "Bu yorumu güncelleyemezsiniz, çünkü sizin yorumunuz değil!"}, status=403)

    # 🟡 Gelen veriler ile yorum güncelleniyor
    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        # 🟡 Ortalama puanı güncelle
        place = review.place
        all_reviews = Review.objects.filter(place=place)
        place.rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
        place.total_reviews = all_reviews.count()
        place.save()

        return Response({"message": "Yorum başarıyla güncellendi!", "updated_review": serializer.data}, status=200)
    
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
    
# 🟢 Favorilere Ekleme & Çıkarma Fonksiyonu
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    user = request.user

    # Kullanıcı daha önce eklemiş mi?
    favorite, created = FavoritePlace.objects.get_or_create(user=user, place=place)

    if not created:
        favorite.delete()
        return Response({"message": "Favoriden kaldırıldı!"}, status=200)
    
    return Response({"message": "Favorilere eklendi!"}, status=201)
