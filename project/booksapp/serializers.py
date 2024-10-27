from booksapp.models import *
from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class PartBookSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ["id","name","author","rating"]

    def get_author(self, obj):
        return obj.author.name if obj.author else None

class FullBookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genre = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = '__all__'
    
    def get_author(self, obj):
        return obj.author.name if obj.author else None
    
    def get_genre(self, obj):
        return obj.genre.genre_name if obj.genre else None

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','password']
    
    def create(self, validated_data):
        user = super().create(validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()
        return user
    
    def update(self,instance,validated_data):
        user = super().update(instance,validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()
        return user

class BookRatingSerializer(serializers.ModelSerializer):
    book_id = PartBookSerializer()
    class Meta:
        model = BookRating
        fields = ["book_id","rating"]




