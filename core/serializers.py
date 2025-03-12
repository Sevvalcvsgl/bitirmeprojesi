from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Place, Review  # Mekan ve yorum modellerini içe aktar

# Kullanıcı Serializer'ı (Register ve Login işlemleri için)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Şifreyi JSON çıktısında göstermemek için

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

# Mekan Serializer'ı (Mekan bilgilerini JSON'a çevirmek için)
class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

# Yorum Serializer'ı (Kullanıcıların mekanlara yaptığı yorumları JSON'a çevirmek için)
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Kullanıcı adını göster
    place = serializers.StringRelatedField()  # Mekan adını göster

    class Meta:
        model = Review
        fields = ['id', 'user', 'place', 'comment', 'rating', 'created_at']
