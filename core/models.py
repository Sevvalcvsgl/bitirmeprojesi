from django.db import models

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
