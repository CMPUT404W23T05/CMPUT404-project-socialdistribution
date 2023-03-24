from rest_framework import serializers
from .models import *
from .serializers import AuthorSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'author', 'auth_token')
        read_only_fields = ('auth_token',)

    def get_author(self, obj):
        try:
            author = obj.author
        except Author.DoesNotExist:
            author = None

        return AuthorSerializer(author).data
