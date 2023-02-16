from rest_framework import serializers
from .models import Follow, Followers
from authors.models import Author

class AuthorSerializer(serializers.ModelSerializer):

    # get the author's information
    type = serializers.CharField(source = 'object_type')
    id = serializers.UUIDField(source = 'profile_url')
    url = serializers.URLField(source = 'profile_url')
    host = serializers.URLField(source = 'home_host')
    displayName = serializers.CharField(source = 'display_name')
    github = serializers.URLField(source = 'author_github')
    profileImage = serializers.URLField(source = 'profile_image')

    class Meta:
        model = Author
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

class FollowSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source = 'follow_type')
    actor = serializers.JSONField(source = 'author_actor') # the author who is the follower
    object = serializers.JSONField(source = 'author_object') # the author who is being followed
    summary = serializers.CharField(source = 'following_summary')

    class Meta:
        model = Follow
        fields = ['type', 'actor', 'object', 'summary']

class AuthorFollowersSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="followers")
    items = AuthorSerializer(many=True) # a list of the followers

    class Meta:
        model = Author
        fields = ['type', 'items']

    def create(self, validated_data):
        followers_info = validated_data.pop('items')
        create_author = Author.objects.create(**validated_data)
        for follower in followers_info:
            Followers.objects.create(follower_author = create_author,**follower)
        return create_author
 

