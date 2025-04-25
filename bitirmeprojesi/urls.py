"""
URL configuration for bitirmeprojesi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core import views as core_views  # Core views import edildi
from main import views as main_views  # Web sayfası views import edildi
from django.urls import path, include  # include'u ekledik
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin paneli için URL
    path('api/', include('core.urls')),  # API Endpoints için core.urls'ü dahil ediyoruz

    # Web sayfası (Ana sayfa)
    path('', main_views.home, name='home'),  # Ana sayfa için URL

    # API Endpoints (core views kullanılarak)
    path('api/places/', core_views.place_list, name='place_list'),  # Mekan listeleme API
    path('api/reviews/<int:place_id>/', core_views.add_review, name='add_review'),  # Yorum ekleme API
]
