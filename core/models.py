from django.db import models
from django.contrib.auth.models import User  # Kullanıcı modeli
from django.core.validators import MinValueValidator, MaxValueValidator

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('study', 'Study Cafes'),
        ('family', 'Family Places'),
        ('romantic', 'Romantic Place'),
        ('casual', 'Casual Cafes'),
        ('luxury', 'Luxury Cafes'),
        ('outdoor', 'Outdoor Place'),
        ('vegan', 'Vegan Friendly Cafes'),
        ('pet_friendly', 'Pet Friendly Cafes'),
        ('breakfast', 'Breakfast Places'),
        ('dessert', 'Dessert'),
        ('book_cafe', 'Book Cafes'),
        ('cozy', 'Cozy Cafes'),
        ('fast_food', 'Fastfood'),
        ('themed', 'Themed Cafes'),
        ('music', 'Live Music Places'),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    price_range = models.CharField(max_length=20, choices=[('cheap', 'Cheap'), ('medium', 'mMdium'), ('expensive', 'Expensive')], default='medium')
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
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
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



class Comment(models.Model):  # DIŞARI alındı
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    comment_text = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.place.name}"



class Rating(models.Model):  # DIŞARI alındı
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.place} ({self.rating})"
    