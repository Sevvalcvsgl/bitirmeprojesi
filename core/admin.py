from django.contrib import admin
from .models import Place, Review, FavoritePlace 
from .models import Rating
from .models import Comment

admin.site.register(Place)
admin.site.register(Review)
admin.site.register(FavoritePlace)
admin.site.register(Comment)
admin.site.register(Rating)

