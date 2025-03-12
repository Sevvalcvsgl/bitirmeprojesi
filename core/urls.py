from django.urls import path
from .views import place_list, register_user, login_user, add_review, place_reviews

urlpatterns = [
    path('places/', place_list, name='place_list'),
    path('places/<int:place_id>/review/', add_review, name='add_review'),  # Yeni yorum ekleme endpointi
    path('places/<int:place_id>/reviews/', place_reviews, name='place-reviews'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
]
