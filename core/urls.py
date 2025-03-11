from django.urls import path
from .views import place_list, register_user, login_user

urlpatterns = [
    path('places/', place_list, name='place_list'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
]
