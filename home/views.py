from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.http import Http404

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder



class CreatePost(APIView):

    def post(self, request, author_id, format=None):
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
    def post(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        serializer = PostDeSerializer(instance=post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # FOR DELETING EXISITING POST
    def delete(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FollowersList(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/followers
    '''
    def get(self, request, author_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0] 
            serializer = AuthorFollowersSerializer(current_author) # get all the followers
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND) # author id does not exist
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    
class FollowersDetails(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    '''
    def get(self, request, author_id, follower_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
            selected_follower = Author.objects.filter(uid=follower_id)[0]

            follower_info_to_dict = model_to_dict(selected_follower)
            
            if 'id' in follower_info_to_dict:
                del follower_info_to_dict['id']


            follower_info_to_json = json.dumps(follower_info_to_dict, cls=DjangoJSONEncoder)

            # is this author a follower of the current author? Compare the information
            check_follower = current_author.followers_items.filter(author_info = follower_info_to_json)[0]
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_200_OK)
        
    def delete(self, request, author_id, follower_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
            selected_follower = Author.objects.filter(uid=follower_id)[0]
  
            follower_info_to_dict = model_to_dict(selected_follower)
            follower_info_to_json = json.dumps(follower_info_to_dict, cls=DjangoJSONEncoder)

            selected_follower = current_author.followers_items.filter(author_info = follower_info_to_json)[0]
        
        except IndexError: 
            return Response(status=status.HTTP_404_NOT_FOUND)  
        else:
            selected_follower.delete() 
            return Response(status=status.HTTP_204_NO_CONTENT) 

    def put(self, request, author_id, follower_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
            selected_follower = Author.objects.filter(uid=follower_id)[0]
            follower_info_to_json = json.dumps(model_to_dict(selected_follower), cls=DjangoJSONEncoder)
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)  
        else:
            current_author.followers_items.create(author_info = follower_info_to_json)
            return Response(status=status.HTTP_201_CREATED) 
    
class FollowingList(APIView):

    def get(self, request, author_id):
        current_author = Author.objects.filter(uid=author_id)[0]
        author_info_to_json = json.dumps(model_to_dict(current_author), cls=DjangoJSONEncoder)

        # check if the author is the followers_list of the authors
        following_authors = Author.objects.filter(followers_items__author_info = author_info_to_json)

        serializer = AuthorSerializer(following_authors, many=True)
        return Response(serializer.data)

class FriendsList(APIView):

    def get(self, request, author_id):

        current_author = Author.objects.filter(uid=author_id)[0]
        author_info_to_json = json.dumps(model_to_dict(current_author),cls=DjangoJSONEncoder)
        
        following_list = Author.objects.filter(followers_items__author_info= author_info_to_json) # who they're following
        follower_list = current_author.followers_items.all() # who is following them
        list_of_friends = []  

        for following in following_list:
            for follower in follower_list:
                following_id = following.uid # id of the author who is being followed by the current author
                follower_id = uuid.UUID(json.loads(follower.author_info)['uid']) # id of the author who is following the current author
                if following_id == follower_id: 
                    list_of_friends.append(following)

        serializer = AuthorSerializer(list_of_friends, many=True)
        return Response(serializer.data)

class RequestsList(APIView):
    def get(self, request, author_id):

        current_author = Author.objects.filter(uid=author_id)[0]
        author_info_to_dict = json.loads(json.dumps(model_to_dict(current_author), cls=DjangoJSONEncoder))
        
        if 'id' in author_info_to_dict:
            del author_info_to_dict['id']

        # check if any of the Follow objects have the current author as the author that is "being followed"
        follows = Follow.objects.filter(author_object = author_info_to_dict) 
        serializer = FollowSerializer(follows, many = True)
        return Response(serializer.data)

class AuthorList(APIView, PageNumberPagination):
    def get(self, request, format=None):
        authors = Author.objects.all()

        self.page = request.query_params.get('page', 1)
        self.page_size = request.query_params.get('size', 20)

        results = self.paginate_queryset(authors, request, view=self)
        serializer = AuthorSerializer(results, many=True)
        response = {
                'type': 'authors',
                'items': serializer.data
                }
        return Response(response)



