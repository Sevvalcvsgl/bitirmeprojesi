from django.contrib import admin

from django.contrib import admin
from .models import Place  # Modelimizi içe aktardık

admin.site.register(Place)  # Admin paneline ekledik
