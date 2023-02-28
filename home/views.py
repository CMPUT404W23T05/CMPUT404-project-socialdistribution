from django.shortcuts import render
from .models import Post
from .serializers import PostSerializer

from rest_framework.views import APIView
from rest_framework.response import Response


from datetime import datetime
import json

'''
view for login
'''
def login(request):
    pass


'''
default view for home page
'''
def index(request):
    pass


# Creation URL ://service/authors/{AUTHOR_ID}/posts/
# POST [local] create a new post but generate a new id
'''
page for viewing author posts and creating a new post
'''
def posts(request):
    if request.method == 'POST':
        # parse the json data from req body into python dict
        body_str = request.body.decode('utf-8')
        data = json.loads(body_str)
        if data['type'] == 'post':
            response = Post.objects.create_post(data)

class GetLatestPosts(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()[0:5]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
