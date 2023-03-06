from rest_framework import serializers
from .models import *
from django.core.files.base import ContentFile
import base64
import uuid
import imghdr
from django.contrib.auth import authenticate


# need to pip install rest_framework
# To convert your queries to or from a JSON object (useful when connecting with groups)

# Reference: https://stackoverflow.com/questions/31690991/uploading-base64-images-using-modelserializers-in-django-django-rest-framework
# class Base64ImageField(serializers.ImageField):

#     def to_internal_value(self, data):
#         try:
#             decoded_file = base64.b64decode(data)
#         except TypeError:
#             self.fail('invalid_image')

#         file_name = 'test_image' + str(uuid.uuid4())[:5] # change to 12 later
#         file_extension = self.get_file_extension(file_name, decoded_file)
#         complete_file_name = '%s.%s' % (file_name, file_extension)
#         img_file = ContentFile(decoded_file, name=complete_file_name)

#         return super(Base64ImageField, self).to_internal_value(img_file)

#     def get_file_extension(self, file_name, decoded_file):
#         extension = imghdr.what(file_name, decoded_file)
#         extension = 'jpg' if extension == 'jpeg' else extension
#         return extension


class AuthorSerializer(serializers.ModelSerializer):

    # get the author's information
    type = serializers.CharField(source='object_type')
    id = serializers.UUIDField(source='uid')
    url = serializers.URLField(source='profile_url')
    host = serializers.URLField(source='home_host')
    displayName = serializers.CharField(source='display_name')
    github = serializers.URLField(source='author_github', allow_null=True, allow_blank=True)
    profileImage = serializers.URLField(source='profile_image')

    class Meta:
        model = Author
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']



class PostSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='object_type')
    id = serializers.UUIDField(source='post_id')
    source = serializers.URLField(source='post_source')
    origin = serializers.URLField(source='post_origin')
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
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType',
                  'image', 'content', 'author', 'count', 'comments', 'published',
                  'visibility', 'unlisted']

class PostDeSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='object_type')
    id = serializers.UUIDField(source='post_id')
    source = serializers.URLField(source='post_source')
    origin = serializers.URLField(source='post_origin')
    contentType = serializers.CharField(source='content_type', required=False)
    image = CharField(required=False, allow_blank=True, allow_null=True)
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    author = AuthorSerializer() 
    count = serializers.IntegerField(source='comment_count')
    published = serializers.DateTimeField(source='pub_date', required=False)
    unlisted = serializers.BooleanField(source='is_unlisted')

    class Meta:
        model = Post
        # add 'categories' later
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType',
                  'image', 'content', 'author', 'count', 'comments', 'visibility',
                  'unlisted', 'published']

    def get_author(self, author_uid):
        try:
            return Author.objects.get(uid=author_uid)
        except Author.DoesNotExist:
            raise serializers.ValidationError('Author not found, uid: ', author_uid)

    def create(self, validated_data):
        author_obj = validated_data.pop('author')
        author_uid = author_obj['uid']
        author = self.get_author(author_uid)
        validated_data['author'] = author
        return super().create(validated_data)

    def update(self, instance, validated_data):
        author_obj = validated_data.pop('author')
        author_uid = author_obj['uid']
        author = self.get_author(author_uid)
        validated_data['author'] = author
        return super().create(validated_data)

    def validate(self, attrs):
        if 'content' not in attrs and 'image' not in attrs:
            raise serializers.ValidationError("At least one of 'body' or 'image' is required.")
        return attrs



class CommentSerializer(serializers.ModelSerializer):

    type = serializers.CharField(default='comment', source='object_type')
    post_id = serializers.UUIDField()
    id = serializers.UUIDField(source='comment_id')
    author = AuthorSerializer()
    comment = serializers.CharField(source='content')
    contentType = serializers.CharField(source='content_type')
    published = serializers.DateTimeField(source='pub_date', required=False)

    class Meta:
        model = Comment
        fields = ['type', 'post_id', 'id', 'author', 'comment', 'contentType', 'published']


    def get_author(self, author_uid):
        try:
            return Author.objects.get(uid=author_uid)
        except Author.DoesNotExist:
            raise serializers.ValidationError('Author not found, uid: ', author_uid)

    def create(self, validated_data):
        author_obj = validated_data.pop('author')
        author_uid = author_obj['uid']
        author = self.get_author(author_uid)
        validated_data['author'] = author
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='object_type')
    summary = serializers.CharField(source='like_summary')
    author = serializers.JSONField(source='author_object') # the author who is the follower
    object = serializers.URLField(source='obj') # the post/comment that was liked

    class Meta:
        model = Like
        fields = ['context', 'type', 'summary', 'author', 'object']

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
                'score': 'This field is required.'
            })
        if not liked_items:
            raise serializers.ValidationError({
                'player_name': 'This field is required.'
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
        for item in instance.inbox.all():
            items_list.append(item.inbox_item) # add all the "notifications"
        return {
            'type': 'inbox',
            'author': instance.profile_url,
            'items': items_list
        }


class FollowSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='follow_type')
    actor = serializers.JSONField(source='author_actor') # the author who is the follower
    object = serializers.JSONField(source='author_object') # the author who is being followed
    summary = serializers.CharField(source='following_summary')

    class Meta:
        model = Follow
        fields = ['type', 'actor', 'object', 'summary']

# ---------------------- Followers Serializer ----------------------------------
class AuthorFollowersSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="followers")
    followers_items = AuthorSerializer(many=True) # a list of the followers

    class Meta:
        model = Author
        fields = ['type', 'followers_items']

    def create(self, validated_data):
        followers_info = validated_data.pop('followers_items')
        create_author = Author.objects.create(**validated_data)
        for follower in followers_info:
            Followers.objects.create(follower_author = create_author,**follower)
        return create_author

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return_data = {}
        return_data.update({
                'type': data['type'],
                'items': data['followers_items']})
        return return_data
