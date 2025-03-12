from django.db import models
from django.contrib.auth.models import User  # Kullanıcı modeli

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('study', 'Çalışma Kafesi'),
        ('family', 'Aile Kafesi'),
        ('romantic', 'Romantik Mekan'),
        ('casual', 'Sıradan Kafe'),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)

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
