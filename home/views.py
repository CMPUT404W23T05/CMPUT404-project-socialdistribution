from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


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
class CreatePost(APIView):
    def post(self, request, format=None):
        serializer = PostDeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPosts(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()[0:5]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

# class PostDetail(APIView):
#     def get_object(self, ):
