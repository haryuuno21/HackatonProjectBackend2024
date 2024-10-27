from booksapp.models import *
from rest_framework import serializers

class PartBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id","book_name","author_name","photo_url","rating"]

class FullBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

class BookRatingSerializer(serializers.ModelSerializer):
    book_id = PartBookSerializer()
    class Meta:
        model = Book
        fields = ["book_id","user_id","rating"]

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