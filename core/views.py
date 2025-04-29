import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Place, Review, FavoritePlace, Rating, Comment
from .serializers import (
    UserSerializer, ReviewSerializer, PlaceSerializer,
    RatingSerializer, CommentSerializer
)

# 🟢 Mekan Listeleme
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

# ✅ Kategori Listesi
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Place.CATEGORY_CHOICES
    formatted = [{'key': key, 'label': label} for key, label in categories]
    return Response(formatted)

# ✅ Kullanıcı Kaydı
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Kullanıcı başarıyla oluşturuldu!', 'user': serializer.data}, status=201)
    return Response(serializer.errors, status=400)

# ✅ Kullanıcı Girişi (JWT Token ile)
@api_view(['POST'])
@permission_classes([AllowAny])
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
    return Response({'error': 'Geçersiz kullanıcı adı veya şifre!'}, status=400)

# ✅ Şifre Değiştirme
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old = request.data.get('old_password')
    new = request.data.get('new_password')

    if not user.check_password(old):
        return Response({'error': 'Eski şifre yanlış.'}, status=400)
    if not new or len(new) < 6:
        return Response({'error': 'Yeni şifre en az 6 karakter olmalı.'}, status=400)

    user.set_password(new)
    user.save()
    return Response({'message': 'Şifre başarıyla değiştirildi.'}, status=200)

# ✅ Yorum Ekleme
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    if Review.objects.filter(user=request.user, place=place).exists():
        return Response({"error": "Bu mekana zaten yorum yaptınız!"}, status=400)

    review = Review.objects.create(
        user=request.user,
        place=place,
        comment=request.data.get('comment'),
        rating=request.data.get('rating')
    )

    all_reviews = Review.objects.filter(place=place)
    place.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    place.total_reviews = all_reviews.count()
    place.save()

    return Response(ReviewSerializer(review).data, status=201)

# ✅ Yorum Silme
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        return Response({"error": "Bu sizin yorumunuz değil!"}, status=403)
    review.delete()
    return Response({"message": "Yorum silindi!"}, status=200)

# ✅ Yorum Güncelleme
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        return Response({"error": "Bu sizin yorumunuz değil!"}, status=403)

    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        all_reviews = Review.objects.filter(place=review.place)
        review.place.rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
        review.place.total_reviews = all_reviews.count()
        review.place.save()
        return Response({"message": "Yorum güncellendi!", "review": serializer.data}, status=200)
    return Response(serializer.errors, status=400)

# ✅ Mekan Yorumları
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def place_reviews(request, place_id):
    reviews = Review.objects.filter(place__id=place_id)
    return Response(ReviewSerializer(reviews, many=True).data)

# ✅ Favorilere Ekleme/Çıkarma
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    favorite, created = FavoritePlace.objects.get_or_create(user=request.user, place=place)
    if not created:
        favorite.delete()
        return Response({"message": "Favoriden kaldırıldı!"}, status=200)
    return Response({"message": "Favorilere eklendi!"}, status=201)

# ✅ Kullanıcıya Ait Yorumlar
@api_view(['GET'])
def get_user_comments(request, username):
    user = get_object_or_404(User, username=username)
    comments = Comment.objects.filter(user=user)
    return Response(CommentSerializer(comments, many=True).data)

# ✅ Kullanıcıya Ait Puanlamalar
@api_view(['GET'])
def get_user_ratings(request, username):
    user = get_object_or_404(User, username=username)
    ratings = Rating.objects.filter(user=user)
    return Response(RatingSerializer(ratings, many=True).data)

# ✅ Rating ViewSet
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ✅ Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
