from rest_framework import serializers
from home.serializers import AuthorSerializer, CommentSerializer
from home.models import Post, Comment

class PostForRemoteSerializer(serializers.ModelSerializer):
    
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
                'unlisted': data['unlisted']})
        # add comment src?
        comments = Comment.objects.filter(post_id=data['_id'])[:5]
        serializer = CommentSerializer(comments, many=True)
        comment_src_object = {
                "type": "comments",
                "page": 1,
                "size": 5,
                "post": data['id'],
                "id": data['id'] + '/comments',
                "comments": serializer.data
                }
        return_data['commentSrc'] = comment_src_object
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
        
        data = super().to_representation(instance)

        # description cannot be blank (if blank, add something in like the content)
        if not data["description"]:
            data["description"] = data["content"]

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