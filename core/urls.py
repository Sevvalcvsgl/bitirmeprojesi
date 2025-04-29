from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import RatingViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'ratings', RatingViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    # 🟢 Mekan Listeleme ve Filtreleme
    path('places/', views.place_list, name='place-list'),

    # 🟢 Favorilere Ekleme / Çıkarma
    path('places/<int:place_id>/favorite/', views.toggle_favorite, name="toggle_favorite"),

    # 🟢 Mekan Yorumları
    path('places/<int:place_id>/reviews/', views.place_reviews, name='place_reviews'),
    path('places/<int:place_id>/review/', views.add_review, name='add_review'),  
    path('places/<int:review_id>/review/delete/', views.delete_review, name='delete_review'),  
    path('places/<int:review_id>/review/update/', views.update_review, name='update_review'),  

    # 🟢 Kullanıcı Kayıt ve Giriş
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('change_password/', views.change_password, name='change_password'),

    # 🟢 Kullanıcıya Ait Yorumlar ve Puanlar
    path('api/comments/<str:username>/', views.get_user_comments, name='user-comments'),
    path('api/ratings/<str:username>/', views.get_user_ratings, name='user-ratings'),

    # 🟢 Kategori Listesi
    path('categories/', views.category_list, name='category_list'),

    # 🔹 ViewSet'ler için otomatik URL'ler
    path('', include(router.urls)),
]
