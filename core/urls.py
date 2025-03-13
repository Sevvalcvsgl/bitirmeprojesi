from django.urls import path
from .views import place_list, register_user, login_user, add_review, place_reviews , delete_review, update_review

urlpatterns = [
    path('places/', place_list, name='place_list'),
    path('places/', views.place_list, name='place_list'),  # 🟡 Mekan listeleme rotası
    path('places/<int:place_id>/reviews/', views.place_reviews, name='place_reviews'),  # 🟡 Mekan yorumları
    path('places/<int:place_id>/review/', add_review, name='add_review'),  # Yeni yorum ekleme endpointi
    path('places/<int:place_id>/reviews/', place_reviews, name='place-reviews'),
    path('places/<int:review_id>/review/delete/', delete_review, name='delete_review'),  # Yorum silme endpointi
    path('places/<int:review_id>/review/update/', update_review, name='update_review'),  # Yorum güncelleme endpointi
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
]
