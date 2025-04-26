from django.urls import path
from . import views  # views modülünü ekledik





urlpatterns = [
    # 🟢 Mekan Listeleme ve Filtreleme
    path('places/', views.place_list, name='place_list'),  

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
    
    path('categories/', views.category_list, name='category_list'), 

   # path('hello/', views.test_api),  # http://127.0.0.1:8000/api/hello/ adresine bu fonksiyon gider 
  
  
  
  
]
