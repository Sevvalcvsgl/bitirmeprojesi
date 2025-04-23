import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Place, Review, FavoritePlace
from .serializers import UserSerializer, ReviewSerializer, PlaceSerializer

# 🟢 Mekan Listeleme Fonksiyonu — ARTIK GİRİŞ GEREKMİYOR
@api_view(['GET'])
@permission_classes([AllowAny])
def place_list(request):
    category_filter = request.GET.get('category')
    min_rating = request.GET.get('min_rating')
    search_query = request.GET.get('search')
    location_filter = request.GET.get('location')
    sort_by = request.GET.get('sort_by', '-rating')
    price_filter = request.GET.get('price')
    wifi_filter = request.GET.get('wifi')

    places = Place.objects.all()

    if category_filter:
        categories = category_filter.split(',')
        places = places.filter(category__in=categories)

    if min_rating:
        try:
            min_rating = float(min_rating)
            places = places.filter(rating__gte=min_rating)
        except ValueError:
            return Response({"error": "Geçersiz min_rating değeri!"}, status=400)

    if search_query:
        places = places.filter(name__icontains=search_query)

    if location_filter:
        places = places.filter(location__icontains=location_filter)

    if price_filter:
        price_levels = price_filter.split(',')
        places = places.filter(price__in=price_levels)

    if wifi_filter is not None:
        if wifi_filter.lower() == "true":
            places = places.filter(has_wifi=True)
        elif wifi_filter.lower() == "false":
            places = places.filter(has_wifi=False)

    valid_sort_fields = ['name', '-name', 'rating', '-rating', 'total_reviews', '-total_reviews']
    if sort_by in valid_sort_fields:
        places = places.order_by(sort_by)
    else:
        places = places.order_by('-rating')

    serializer = PlaceSerializer(places, many=True)
    return Response(serializer.data)

# 🟢 ✅ Kategorileri Listeleme Fonksiyonu
@api_view(['GET'])
def category_list(request):
    categories = Place.CATEGORY_CHOICES
    formatted_categories = [{'key': key, 'label': label} for key, label in categories]
    return Response(formatted_categories)

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
        from django.contrib.auth import login
        login(request, user)

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Giriş başarılı!',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=200)
    else:
        return Response({'error': 'Geçersiz kullanıcı adı veya şifre!'}, status=400)

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

    all_reviews = Review.objects.filter(place=place)
    place.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    place.total_reviews = all_reviews.count()
    place.save()

    return Response(ReviewSerializer(review).data, status=201)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Yorum bulunamadı!"}, status=404)

    if review.user != request.user:
        return Response({"error": "Bu yorumu silemezsiniz, çünkü bu sizin yorumunuz değil!"}, status=403)

    review.delete()
    return Response({"message": "Yorum başarıyla silindi!"}, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return Response({"error": "Bu yorumu güncelleyemezsiniz, çünkü sizin yorumunuz değil!"}, status=403)

    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        place = review.place
        all_reviews = Review.objects.filter(place=place)
        place.rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
        place.total_reviews = all_reviews.count()
        place.save()

        return Response({"message": "Yorum başarıyla güncellendi!", "updated_review": serializer.data}, status=200)

    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_reviews(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    reviews = Review.objects.filter(place=place)
    
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    user = request.user

    favorite, created = FavoritePlace.objects.get_or_create(user=user, place=place)

    if not created:
        favorite.delete()
        return Response({"message": "Favoriden kaldırıldı!"}, status=200)

    return Response({"message": "Favorilere eklendi!"}, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_detail(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    data = {
        "id": place.id,
        "name": place.name,
        "latitude": place.latitude,
        "longitude": place.longitude,
    }
    return Response(data, status=200)
