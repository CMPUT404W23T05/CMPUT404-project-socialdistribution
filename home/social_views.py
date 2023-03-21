
from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import permission_classes
from django.http import HttpResponse, Http404
from djoser.views import TokenCreateView

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder


class FollowersList(APIView):
    '''
    Get a list of authors who are AUTHOR_ID’s followers (local, remote)

    Returns a 200 OK, otherwise returns 404 Not Found if the author does not exist
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        current_author =  author = self.get_object(author_id) # get the first match
        serializer = AuthorFollowersSerializer(current_author) # get all the followers
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FollowersDetails(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def check_follower(self, current_author, follower_info):
        '''
        Checks if a specific author is following the current author
        '''
        try:
            return current_author.followers_items.filter(author_info = follower_info)[0]
        except: # follower does not exist (i.e. we get an IndexError)
            raise Http404 
        
    def get(self, request, author_id, follower_id):
        '''
        Checks to see if follower_id is a follower of author_id (local, remote)

        Returns a status code of 200 OK with one of the following response body:

        {"exists": "true"}
        OR
        {"exists": "false"}

        Else, it returns a status code of 404
        '''
        # get the first match
        current_author = self.get_object(author_id)
        selected_follower = self.get_object(follower_id)

        # turning our data into bytes and then to a string
        follower_serializer = AuthorSerializer(selected_follower)
        author_data = json.dumps(follower_serializer.data)
        follower_data_dict = json.loads(author_data)

        # is this author a follower of the current author? Compare the information
        check_follower = current_author.followers_items.filter(author_info = follower_data_dict)

        response_body = {}
        if len(check_follower) > 0: # the author does follow the current author
            response_body["exists"] = "true"
        else:
            response_body["exists"] = "false"

        return Response(response_body, status=status.HTTP_200_OK)
        
    def delete(self, request, author_id, follower_id):
        '''
        Removes follower_id as a follower of author_id (local)

        If author_id or follower_id does not exist, then status code = 404 Not Found,
        else 204 No Content
        '''
        # get the author and the follower
        current_author = self.get_object(author_id)
        selected_follower = self.get_object(follower_id)
        
        # turning our data into bytes, to string, then a dict
        author_serializer = AuthorSerializer(current_author)
        current_author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(current_author_data)

        follower_serializer = AuthorSerializer(selected_follower)
        follower_author_data = json.dumps(follower_serializer.data)
        follower_data_dict = json.loads(follower_author_data)

        # update the status of the follow request object (remove follower = we unbefriend that person aka they no longer follow us)
        get_follow_object = Follow.objects.filter(author_object=author_data_dict).filter(author_actor=follower_data_dict)
        if len(get_follow_object) > 0:
            get_follow_object[0].state = "Declined"
            get_follow_object[0].save(update_fields=["state"])

        selected_follower = self.check_follower(current_author, follower_data_dict)

        # if everything above is successful
        selected_follower.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT) 

    
    @permission_classes([IsAuthenticated])
    def put(self, request, author_id, follower_id):
        '''
        Add follower_id as a follower of author_id (must be authenticated, local)

        If author_id or follower_id does not exist, then status code = 404 Not Found,
        else 200 OK (the follower has been added) or 409 Conflict (the follower already exists), or
        400 Bad Request (maybe you're making the author follow itself?)
        '''
        if author_id == follower_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)  
                 
        # get the author and the follower
        current_author = self.get_object(author_id)
        selected_follower = self.get_object(follower_id)

        # turning our data into bytes, to a string, then dict
        follower_serializer = AuthorSerializer(selected_follower)
        follower_data = json.dumps(follower_serializer.data)
        follower_data_dict = json.loads(follower_data)

        # checks if follower already exists (to avoid duplicates)
        does_follower_exist = current_author.followers_items.filter(author_info = follower_data_dict)
        
        if len(does_follower_exist) > 0: # this follower already exists
            return Response(status=status.HTTP_409_CONFLICT) 

        else:
            current_author.followers_items.create(author_info = follower_data_dict)
            return Response(status=status.HTTP_201_CREATED) 
    
class FollowingList(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/following
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        '''
        Get a list of authors that the current author is following (extra - not in spec, local)

        Returns a list of Author objects[{"type":"author"...},..] and a status code of 200 OK,
        else returns a status code of 404 Not Found
        '''
        current_author = self.get_object(author_id)

        # turning our data into bytes, to a string, then to a dict
        author_serializer = AuthorSerializer(current_author)
        author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(author_data)

        # check if the author is the followers_list of the authors
        following_authors = Author.objects.filter(followers_items__author_info = author_data_dict)
 
        # returns a list of Author objects that the current author is following
        serializer = AuthorSerializer(following_authors, many=True)
        
        # convert serializer return list to string, then string to a dict
        following_data = json.dumps(serializer.data)
        following_list = json.loads(following_data)
        following_json = {"type": "following", "items": following_list}
        return Response(following_json)

class FriendsList(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/friends
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        '''
        Gets a list of the author's friends, where they follow each other (extra - not in spec, local)

        Returns a list of Author objects[{"type":"author"...},..] and a status code of 200 OK, 
        else, returns a status code of 404 Not Found
        '''
        current_author = self.get_object(author_id)

        # turning our data into bytes, to a string, and then to a regular dict
        author_serializer = AuthorSerializer(current_author)
        author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(author_data)

        # check who the current author is following, and who is following
        # the current author
        following_list = Author.objects.filter(followers_items__author_info = author_data_dict)
        follower_list = current_author.followers_items.all() # who is following them

        list_of_friends = []  

        for following in following_list: # for each author that the current author is following
            for follower in follower_list: # for each author that is following the current author

                following_id = following.profile_url # id of the author who is being followed by the current author
                follower_id = follower.author_info['url'] 
                
                # this particular author is following the current author
                # and is being followed by the current author
                if following_id == follower_id: 
                    list_of_friends.append(following)

        serializer = AuthorSerializer(list_of_friends, many=True)

        friends_data = json.dumps(serializer.data)
        friends_list = json.loads(friends_data)
        friends_json = {"type": "friends", "items": friends_list}
        return Response(friends_json, status=status.HTTP_200_OK)
