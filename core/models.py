from django.db import models
from django.contrib.auth.models import User  # Kullanıcı modeli

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('study', 'Çalışma Kafesi'),
        ('family', 'Aile Kafesi'),
        ('romantic', 'Romantik Mekan'),
        ('casual', 'Sıradan Kafe'),
        ('luxury', 'Lüks Kafe'),
        ('outdoor', 'Açık Hava Mekanı'),
        ('vegan', 'Vegan Dostu Kafe'),
         ('pet_friendly', 'Evcil Hayvan Dostu'),
        ('breakfast', 'Kahvaltı Mekanı'),
        ('dessert', 'Tatlıcı / Pastane'),
        ('book_cafe', 'Kitap Kafesi'),
        ('cozy', 'Samimi ve Sakin Mekan'),
        ('fast_food', 'Hızlı Yemek'),
        ('themed', 'Tematik Kafe'),
        ('music', 'Canlı Müzikli Mekan'),   
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    price_range = models.CharField(max_length=20, choices=[('cheap', 'Uygun'), ('medium', 'Orta'), ('expensive', 'Pahalı')])
    has_wifi = models.BooleanField(default=False)

      # 🟢 Yeni eklenen alanlar:
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Yorumu yapan kullanıcı
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews")  # Yoruma ait mekan
    comment = models.TextField()  # Kullanıcının yorumu
    rating = models.IntegerField()  # 1-5 arasında bir puan
    created_at = models.DateTimeField(auto_now_add=True)  # Yorumun yapıldığı zaman

    def __str__(self):
        return f"{self.user.username} - {self.place.name} - {self.rating}⭐"

# 🟢 Kullanıcı Favorileri Modeli
class FavoritePlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")  # Kullanıcı
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="favorited_by")  # Favori mekan

    class Meta:
        unique_together = ('user', 'place')  # Aynı kullanıcı bir mekanı birden fazla ekleyemesin

    def __str__(self):
        return f"{self.user.username} - {self.place.name} (Favori)"
#konum entegrasyonu        
class Place(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()  # Enlem
    longitude = models.FloatField()  # Boylam
