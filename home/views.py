from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from rest_framework.decorators import permission_classes
from djoser.views import TokenCreateView


class CreatePost(APIView):
    # @permission_classes([IsAuthenticated])
    def post(self, request, author_id, format=None):
        try:
            Author.objects.get(uid=author_id)
        except Author.DoesNotExist:
                raise Http404
        serializer = PostDeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostList(APIView, PageNumberPagination):
    def get(self, request, author_id, format=None):
        posts = Post.objects.filter(visibility='PUBLIC')

        self.page = request.query_params.get('page', 1)
        self.page_size = request.query_params.get('size', 20)

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        # return self.get_paginated_response(serializer.data    
        return Response(serializer.data)        


class PostDetail(APIView):
    def get_object(self, post_id):
        try:
            return Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            raise Http404

        # FOR RETRIEVING THE DETAILS OF A GIVEN POST
    def get(self, request, post_id, author_id, format=None):
        product = self.get_object(post_id)
        serializer = PostSerializer(product)
        return Response(serializer.data)

        # PUT DOES NOT WORK CURRENTLY - for creating a post from another node in db
    def put(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        serializer = PostDeSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # FOR EDITING EXISTING POST
    @permission_classes([IsAuthenticated])
    def post(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        serializer = PostDeSerializer(instance=post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # FOR DELETING EXISITING POST
    @permission_classes([IsAuthenticated])
    def delete(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthorList(APIView, PageNumberPagination):
    def get(self, request, format=None):
        authors = Author.objects.all()

        self.page = request.query_params.get('page', 1)
        self.page_size = request.query_params.get('size', 20)

        results = self.paginate_queryset(authors, request, view=self)
        serializer = AuthorSerializer(results, many=True)
        response = {
                "type": "authors",
                "items": serializer.data
                }
        return Response(response)

class CommentList(APIView, PageNumberPagination):
    def get(self, request, post_id, author_id, format=None):
        comments = Comment.objects.filter(post_id=post_id)

        self.page = request.query_params.get('page', 1)
        self.page_size = request.query_params.get('size', 5)

        results = self.paginate_queryset(comments, request, view=self)
        serializer = CommentSerializer(results, many=True)
        response = {
                "type": "comments",
                "page": self.page.number,
                "size": self.page_size,
                "post": request.build_absolute_uri().rstrip('/comments'),
                "id": request.build_absolute_uri(),
                "comments": serializer.data
                }

        return Response(response)

    # @permission_classes([IsAuthenticated])
    def post(self, request, post_id, author_id, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


