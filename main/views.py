from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Bitirme Projesi Ana Sayfası</h1><p>Hoş geldiniz!</p>")