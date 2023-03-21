from rest_framework import routers,serializers,viewsets
from .models import *
from django.core.files.base import ContentFile
import base64
import uuid
import imghdr
from django.contrib.auth import authenticate
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from urllib.parse import urlparse


# need to pip install rest_framework
# To convert your queries to or from a JSON object (useful when connecting with groups)


class AuthorSerializer(serializers.ModelSerializer):

    # get the author's information
    type = serializers.CharField(source='object_type')
    id = serializers.URLField(source='url_id')
    _id = serializers.UUIDField(source='author_id', required=False)
    url = serializers.URLField(source='profile_url')
    host = serializers.URLField(source='home_host')
    displayName = serializers.CharField(source='display_name')
    github = serializers.URLField(source='author_github', allow_null=True, allow_blank=True)
    profileImage = serializers.URLField(source='profile_image')

    class Meta:
        model = Author
        fields = ['type', 'id', '_id', 'url', 'host', 'displayName', 'github', 'profileImage']

    def validate(self, attrs):     
        # check if _id is given, if not parse id for _id
        if 'author_id' not in attrs:
            url = attrs['url_id']
            parsed_url = urlparse(url)
            author_id = parsed_url.path.split('/')[-1]   # grabs the last path value, which should be the author uuid

            # I am assuming the url is valid and not checking (ADD BUG TESTING HERE LATER TO ENSURE NO ERROR)
            # if not blah blah:
            #   raise serializers.ValidationError("Could not extract uuid from url in 'id'. Are you sure 'id' is valid?")

            attrs['author_id'] = author_id

        return attrs


class PostSerializer(serializers.ModelSerializer):
    
    type = serializers.CharField(source='object_type')
    id = serializers.URLField(source='url_id')
    _id = serializers.UUIDField(source='post_id')
    source = serializers.URLField(source='post_source', required=False)
    origin = serializers.URLField(source='post_origin', required=False)
    contentType = serializers.CharField(source='content_type', required=False)
    image = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    author = AuthorSerializer()
    count = serializers.IntegerField(source='comment_count')    
    published = serializers.DateTimeField(source='pub_date')
    unlisted = serializers.BooleanField(source='is_unlisted')

    class Meta:
        model = Post
        # add 'categories' later
        fields = ['type', 'title', 'id', '_id', 'source', 'origin', 'description', 'contentType',
                  'image', 'content', 'author', 'count', 'comments', 'published',
                  'visibility', 'unlisted']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        comments = Comment.objects.filter(post_id=representation['_id'])[:5]
        serializer = CommentSerializer(comments, many=True)
        comment_src_object = {
                "type": "comments",
                "page": 1,
                "size": 5,
                "post": representation['id'],
                "id": representation['id'] + '/comments',
                "comments": serializer.data
                }
        representation['commentSrc'] = comment_src_object
        return representation


class PostDeSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='object_type')
    id = serializers.URLField(source='url_id')
    _id = serializers.UUIDField(source='post_id', required=False)
    source = serializers.URLField(source='post_source', required=False)
    origin = serializers.URLField(source='post_origin', required=False)
    contentType = serializers.CharField(source='content_type')
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    author = AuthorSerializer() 
    count = serializers.IntegerField(source='comment_count')
    published = serializers.DateTimeField(source='pub_date', required=False)
    unlisted = serializers.BooleanField(source='is_unlisted')

    class Meta:
        model = Post
        # add 'categories' later
        fields = ['type', 'title', 'id', '_id', 'source', 'origin', 'description', 'contentType',
                  'image', 'content', 'author', 'count', 'comments', 'visibility',
                  'unlisted', 'published']

    def get_author(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise serializers.ValidationError('Author not found, author_id: ', author_id)

    def create(self, validated_data):
        author_obj = validated_data.pop('author')
        author_id = author_obj['author_id']
        author = self.get_author(author_id)
        validated_data['author'] = author
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # uncomment this line if and when you want to allow partial update() using partial=True in serializer call
        # validated_data.setdefault('post_id', instance.post_id)
        author_obj = validated_data.pop('author')
        author_id = author_obj['author_id']
        author = self.get_author(author_id)
        validated_data['author'] = author
        return super().update(instance, validated_data)

    def validate(self, attrs):
        if 'content' not in attrs and 'image' not in attrs:
            raise serializers.ValidationError("field missing. at least one of 'body' or 'image' is required.")

        # check if _id is given, if not parse id for _id
        if 'post_id' not in attrs:
            url = attrs['url_id']
            parsed_url = urlparse(url)
            post_id = parsed_url.path.split('/')[-1]   # grabs the last path value, which should be the post uuid

            # I am assuming the url is valid and not checking (ADD BUG TESTING HERE LATER TO ENSURE NO ERROR)
            # if not blah blah:
            #   raise serializers.ValidationError("Could not extract uuid from url in 'id'. Are you sure 'id' is valid?")

            attrs['post_id'] = post_id
        
        return attrs


    
class CommentSerializer(serializers.ModelSerializer):

    type = serializers.CharField(default='comment', source='object_type')
    id = serializers.URLField(source='url_id')
    _id = serializers.UUIDField(source='comment_id', required=False)
    post = serializers.UUIDField(source='post_id', required=False)
    author = AuthorSerializer()
    comment = serializers.CharField(source='content')
    contentType = serializers.CharField(source='content_type')
    published = serializers.DateTimeField(source='pub_date', required=False)

    class Meta:
        model = Comment
        fields = ['type', 'id', '_id', 'post', 'author', 'comment', 'contentType', 'published']


    def get_author(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise serializers.ValidationError('Author not found, author_id: ', author_id)

    def create(self, validated_data):
        author_obj = validated_data.pop('author')
        author_id = author_obj['author_id']
        author = self.get_author(author_id)
        validated_data['author'] = author
        return super().create(validated_data)

    def validate(self, attrs):
        if 'comment_id' not in attrs:
            url = attrs['url_id']
            parsed_url = urlparse(url)
            comment_id = parsed_url.path.split('/')[-1]   # grabs the last path value, which should be the comment uuid

            # I am assuming the url is valid and not checking (ADD BUG TESTING HERE LATER TO ENSURE NO ERROR)
            # if not blah blah:
            #   raise serializers.ValidationError("Could not extract uuid from url in 'id'. Are you sure 'id' is valid?")

            attrs['comment_id'] = comment_id

        if 'post_id' not in attrs:
            url = attrs['url_id']
            parsed_url = urlparse(url)
            post_id = parsed_url.path.split('/')[-3]   # grabs the 3rd last path value, which should be the post uuid

            # I am assuming the url is valid and not checking (ADD BUG TESTING HERE LATER TO ENSURE NO ERROR)
            # if not blah blah:
            #   raise serializers.ValidationError("Could not extract uuid from url in 'id'. Are you sure 'id' is valid?")

            attrs['post_id'] = post_id

        return attrs



class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='object_type')
    summary = serializers.CharField(source='like_summary')
    author = serializers.JSONField(source='author_object') # the author who is the follower
    object = serializers.URLField(source='obj') # the post/comment that was liked

    class Meta:
        model = Like
        fields = ['context','type', 'summary', 'author', 'object']


    # Reference: https://stackoverflow.com/questions/51583756/django-rest-framework-modelserializer-fields-whose-names-are-invalid-python-iden
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return_data = {} # update how it's displayed after being serialized
        return_data.update({
                '@context': data['context'],
                'type': data['type'],
                'summary': data['summary'],
                'author': data['author'],
                'object': data['object']})
        return return_data

class AuthorLikesSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="Liked")
    liked_items = LikeSerializer(many=True)

    class Meta:
        model = Author
        fields = ['type', 'liked_items']

    def create(self, validated_data):
        likes_info = validated_data.pop('liked_items')
        create_author = Author.objects.create(**validated_data)
        for like in likes_info:
            Like.objects.create_like(like.context, like.author_object, like.obj)
        return create_author

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return_data = {}
        return_data.update({
                'type': data['type'],
                'items': data['liked_items']})
        return return_data


    def to_internal_value(self, data):
        type = data.get('type')
        liked_items = data.get('items')

        # data validation.
        if not type:
            raise serializers.ValidationError({
                'type': 'This field is required.'
            })
        if not liked_items:
            raise serializers.ValidationError({
                'liked_items': 'This field is required.'
            })

        # returns the validated values
        return {
            'type': type,
            'liked_items': liked_items
        }
# ---------------------- Inbox Serializer ----------------------------------
class InboxItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ['inbox_item']

class AuthorInboxSerializer(serializers.ModelSerializer):
    inbox_items = InboxItemSerializer(many=True)

    class Meta:
        model = Author
        fields = ['inbox_items']

    def create(self, validated_data):
        inbox_info = validated_data.pop('inbox_items')
        create_author = Author.objects.create(**validated_data)
        for item in inbox_info:
            Inbox.objects.create(associated_author = create_author, inbox_item = item.inbox_item)
        return create_author

    def to_representation(self, instance):
        items_list = []
        for item in instance.inbox_items.all():
            items_list.append(item.inbox_item) # add all the "notifications"
        return {
            'type': 'inbox',
            'author': instance.profile_url,
            'items': items_list
        }


class FollowSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source = 'object_type')
    actor = serializers.JSONField(source = 'author_actor') # the author who is the follower
    object = serializers.JSONField(source = 'author_object') # the author who is being followed
    summary = serializers.CharField(source = 'following_summary')

    class Meta:
        model = Follow
        fields = ['type', 'actor', 'object', 'summary']


# ---------------------- Followers Serializer ----------------------------------

class FollowersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follower
        fields = ['author_info']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not isinstance(data['author_info'], dict):
            author_dict = json.loads(data['author_info'])
        else:
            author_dict = data['author_info']
        return_data = {}
        return_data.update({
                'type': author_dict['type'],
                'id': author_dict['id'],
                'host': author_dict['host'],
                'displayName': author_dict['displayName'],
                'url': author_dict['url'],
                'github':author_dict['github'],
                'profileImage': author_dict['profileImage']
                })
        return return_data

class AuthorFollowersSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="followers")
    followers_items = FollowersSerializer(many=True) # a list of the followers

    class Meta:
        model = Author
        fields = ['type', 'followers_items']

    def create(self, validated_data):
        followers_info = validated_data.pop('followers_items')
        create_author = Author.objects.create(**validated_data)
        for follower in followers_info:
            Follower.objects.create(follower_author = create_author, author_info = json.dumps(follower.author_info))
        return create_author

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return_data = {}
        return_data.update({
                'type': data['type'],
                'items': data['followers_items']})
        return return_data
