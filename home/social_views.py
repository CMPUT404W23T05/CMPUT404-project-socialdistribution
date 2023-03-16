# Copyright 2023 John Macdonald, Elena Xu, Jonathan Lo, Gurkirat Singh, and Geoffery Banh

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#         http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



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
    URL: ://service/authors/{AUTHOR_ID}/followers
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(uid=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        '''
        Gets a list of authors who are author_id's followers (local, remote)

        If author_id does not exist, then status code = 404 Not Found,
        else 200 OK
        '''
        current_author =  author = self.get_object(author_id) # get the first match
        serializer = AuthorFollowersSerializer(current_author) # get all the followers
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FollowersDetails(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(uid=author_id)
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

        Else. it returns a status code of 404
        '''
        # get the first match
        current_author = self.get_object(author_id)
        selected_follower = self.get_object(follower_id)

        # turning our data into bytes and then to a string
        serializer = AuthorSerializer(selected_follower)
        json_info = JSONRenderer().render(serializer.data)
        follower_info = json_info.decode("utf-8")

        # is this author a follower of the current author? Compare the information
        check_follower = current_author.followers_items.filter(author_info = follower_info)

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
        
        # turning our data into bytes and then to a string
        serializer = AuthorSerializer(selected_follower)
        json_info = JSONRenderer().render(serializer.data)
        follower_info = json_info.decode("utf-8")
        
        selected_follower = self.check_follower(current_author, follower_info)

        # if everything above is successful
        selected_follower.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT) 

    def put(self, request, author_id, follower_id):
        '''
        Add follower_id as a follower of author_id (must be authenticated, local)

        If author_id or follower_id does not exist, then status code = 404 Not Found,
        else 200 OK (the follower has been added)
        '''
        # get the author and the follower
        current_author = self.get_object(author_id)
        selected_follower = self.get_object(follower_id)

        # turning our data into bytes and then to a string
        serializer = AuthorSerializer(selected_follower)
        json_info = JSONRenderer().render(serializer.data)
        follower_info = json_info.decode("utf-8")
        
        current_author.followers_items.create(author_info = follower_info)
        return Response(status=status.HTTP_201_CREATED) 
    
class FollowingList(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/following
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(uid=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        '''
        Get a list of authors that the current author is following (extra - not in spec, local)

        Returns a list of Author objects[{"type":"author"...},..] and a status code of 200 OK,
        else returns a status code of 404 Not Found
        '''
        current_author = self.get_object(author_id)

        # turning our data into bytes and then to a string
        serializer = AuthorSerializer(current_author)
        json_info = JSONRenderer().render(serializer.data)
        current_author_info = json_info.decode("utf-8")

        # check if the author is the followers_list of the authors
        following_authors = Author.objects.filter(followers_items__author_info = current_author_info)
 
        # returns a list of Author objects that the current author is following
        serializer = AuthorSerializer(following_authors, many=True)
        return Response(serializer.data)

class FriendsList(APIView):
    '''
    URL: ://service/authors/{AUTHOR_ID}/friends
    '''
    def get_object(self, author_id):
        try:
            return Author.objects.get(uid=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        '''
        Gets a list of the author's friends, where they follow each other (extra - not in spec, local)

        Returns a list of Author objects[{"type":"author"...},..] and a status code of 200 OK, 
        else, returns a status code of 404 Not Found
        '''
        current_author = self.get_object(author_id)

        # turning our data into bytes and then to a string
        serializer = AuthorSerializer(current_author)
        json_info = JSONRenderer().render(serializer.data)
        current_author_info = json_info.decode("utf-8")

        # check who the current author is following, and who is following
        # the current author
        following_list = Author.objects.filter(followers_items__author_info = current_author_info)
        follower_list = current_author.followers_items.all() # who is following them

        list_of_friends = []  

        for following in following_list: # for each author that the current author is following
            for follower in follower_list: # for each author that is following the current author

                following_id = following.profile_url # id of the author who is being followed by the current author
                follower_id = (json.loads(follower.author_info))['url'] # convert the string into a dictionary
                
                # this particular author is following the current author
                # and is being followed by the current author
                if following_id == follower_id: 
                    list_of_friends.append(following)

        serializer = AuthorSerializer(list_of_friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestsList(APIView):
    """
    Get all the friend requests of an author
    """
    def get(self, request, author_id):

        try:
            # get the current author and set up its id url
            current_author = Author.objects.filter(uid=author_id)[0]
            get_id_url = current_author.home_host + 'authors/' + str(author_id)

            # find requests with the author in it (as the person being "followed")
            follows = Follow.objects.filter(author_object__url = get_id_url)
        except:
            raise Http404
        else:
            # returns a list of the follows
            serializer = FollowSerializer(follows, many=True) 
            return Response(serializer.data, status=status.HTTP_200_OK)
    
class RequestsDetails(APIView):
    """
    Deletes a friend request when it gets accepted ordeclined
    """
    def delete(self, request, author_id, request_follower_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
            request_author = Author.objects.filter(uid=request_follower_id)[0]

            get_author_url = current_author.home_host + 'authors/' + str(author_id)
            get_request_follower_url = request_author.home_host + 'authors/' + str(request_follower_id)

            # find the appropiate follow object based on our authors from the two urls
            follow = Follow.objects.filter(author_object__url = get_author_url).filter(author_actor__url = get_request_follower_url)[0]
        except:
            raise Http404
        else:
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
