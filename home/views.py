from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder



def login(request):
    pass

def index(request):
    pass


class CreatePost(APIView):
    def post(self, request, author_id, format=None):
        serializer = PostDeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostList(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()[0:5]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class PostDetail(APIView):
    def get_object(self, post_id):
        try:
            return Post.objects.get(post_id=post_id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, post_id, author_id, format=None):
        product = self.get_object(post_id)
        serializer = PostSerializer(product)
        return Response(serializer.data)

        # PUT DOES NOT WORK CURRENTLY
    def put(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        serializer = PostDeSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AuthorList(APIView):
    pass



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
            print(current_author.followers_items.all())
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
        return Response(serializer)

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

        # check if any of the Follow objects have the current author as the author that is "being followed"
        follows = Follow.objects.filter(author_object = author_info_to_dict) 
        serializer = FollowSerializer(follows, many = True)
        return Response(serializer.data)
