from rest_framework import serializers
from home.serializers import AuthorSerializer, CommentSerializer
from home.models import Post, Comment

class PostForRemoteSevenSerializer(serializers.ModelSerializer):
    # uses an extra field called object
    
    type = serializers.CharField(source='object_type')
    id = serializers.URLField(source='url_id')
    _id = serializers.UUIDField(source='post_id')
    source = serializers.URLField(source='post_source', required=False)
    origin = serializers.URLField(source='post_origin', required=False)
    contentType = serializers.CharField(source='content_type', required=False)
    image = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    author = AuthorSerializer()
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    count = serializers.IntegerField(source='comment_count')    
    published = serializers.DateTimeField(source='pub_date')
    unlisted = serializers.BooleanField(source='is_unlisted')

    class Meta:
        model = Post
        # add 'categories' later
        fields = ['type', 'title', 'id', '_id', 'source', 'origin', 'description', 'contentType',
                  'image', 'content', 'author', 'categories', 'count', 'comments', 'published',
                  'visibility', 'unlisted']

    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        return_data = {} # update how it's displayed after being serialized
        return_data.update({
                'type': data['type'],
                'title': data['title'],
                'id': data['id'],
                'source': data['source'],
                'origin': data['origin'],
                'description': data['description'],
                'contentType': data['contentType'],
                'content': data['content'],
                'image': data['image'],
                'author': data['author'],
                'count': data['count'],
                'comments': data['comments'],
                'published': data['published'],
                'visibility': data['visibility'],
                'categories': data['categories'],
                'object': data['id'], # making object as id 
                'unlisted': data['unlisted']})
        return return_data
    

class PostForRemoteTenSerializer(serializers.ModelSerializer):
    
    type = serializers.CharField(source='object_type')
    id = serializers.URLField(source='url_id')
    _id = serializers.UUIDField(source='post_id')
    source = serializers.URLField(source='post_source', required=False)
    origin = serializers.URLField(source='post_origin', required=False)
    contentType = serializers.CharField(source='content_type', required=False)
    image = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    author = AuthorSerializer()
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    count = serializers.IntegerField(source='comment_count')    
    published = serializers.DateTimeField(source='pub_date')
    unlisted = serializers.BooleanField(source='is_unlisted')

    class Meta:
        model = Post
        # add 'categories' later
        fields = ['type', 'title', 'id', '_id', 'source', 'origin', 'description', 'contentType',
                  'image', 'content', 'author', 'count', 'comments', 'categories', 'published',
                  'visibility', 'unlisted']

    def to_representation(self, instance):
        
        data = super().to_representation(instance)

        # description cannot be blank (if blank, add something in like the content)
        if not data["description"]:
            data["description"] = data["content"]
        
        if "categories" in data.keys():
            if data["categories"] == "":
                data["categories"] = ["post"]

        if data["visibility"] == "PUBLIC":
            data["visibility"] = "VISIBLE"

        return_data = {} # update how it's displayed after being serialized
        return_data.update({
                'type': data['type'],
                'title': data['title'],
                'id': data['id'],
                'source': data['source'],
                'origin': data['origin'],
                'description': data['description'],
                'contentType': data['contentType'],
                'content': data['content'],
                'image': data['image'],
                'author': data['author'],
                'categories': data['categories'],
                'count': data['count'],
                'comments': data['comments'],
                'published': data['published'],
                'visibility': data['visibility'],
                'unlisted': data['unlisted']})
        return return_data
    
class CommentForRemoteSerializer(serializers.ModelSerializer):

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


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return_data = {} # update how it's displayed after being serialized
        return_data.update({
                'type': data['type'],
                'id': data['id'],
                'author': data['author'],
                'comment': data['comment'],
                'contentType': data['contentType'],
                'published': data['published']})