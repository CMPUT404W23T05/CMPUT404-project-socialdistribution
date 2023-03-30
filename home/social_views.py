
from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import permission_classes
from django.http import HttpResponse, Http404
from djoser.views import TokenCreateView

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

import requests
import base64


class FollowersList(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/followers
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        """
        Get a list of authors who are AUTHOR_ID’s followers (local, remote)

        Returns a 200 OK, otherwise returns 404 Not Found if the author does not exist
        """
        current_author = self.get_object(author_id) # get the first match
        serializer = AuthorFollowersSerializer(current_author) # get all the followers
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FollowersDetails(APIView):
    """
    URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
        
    def get(self, request, author_id, follower_id):
        """
        Checks to see if follower_id is a follower of author_id (local, remote)
        where follower_id is a url

        Returns a status code of 200 OK with one of the following response body:

        {"exists": "true"}
        OR
        {"exists": "false"}

        Else, it returns a status code of 404
        """
        # get the first match
        current_author = self.get_object(author_id)

        # is this author a follower of the current author? Compare the information
        check_follower = current_author.followers_items.filter(author_info__id = follower_id)

        response_body = {}
        if len(check_follower) > 0: # the author does follow the current author
            response_body["exists"] = "true"
        else:
            response_body["exists"] = "false"

        return Response(response_body, status=status.HTTP_200_OK)
        
    def delete(self, request, author_id, follower_id):
        """
        Removes follower_id as a follower of author_id (local)

        If author_id or follower_id does not exist, then status code = 404 Not Found,
        else 204 No Content
        """
        # get the author and the follower
        current_author = self.get_object(author_id)
        follower_exists = len(current_author.followers_items.filter(author_info__id = follower_id))

        # update the status of the follow request object (remove follower = we unbefriend that person aka they no longer follow us)
        get_follow_object = Follow.objects.filter(author_object__id = current_author.url_id).filter(author_actor__id=follower_id)
        if len(get_follow_object) > 0:
            get_follow_object[0].state = "Declined"
            get_follow_object[0].save(update_fields=["state"])

        if follower_exists:
            # if everything above is successful
            follower_exists[0].delete() 

        return Response(status=status.HTTP_204_NO_CONTENT) 

    
    def put(self, request, author_id, follower_id):
        """
        Add follower_id as a follower of author_id (must be authenticated, local)

        If author_id or follower_id does not exist, then status code = 404 Not Found,
        else 200 OK (the follower has been added) or 409 Conflict (the follower already exists), or
        400 Bad Request (maybe you're making the author follow itself?)
        """ 
        auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
        "https://sd7-api.herokuapp.com/": {"Authorization": "Basic node01:P*ssw0rd!"}}

        our_host = "https://social-t30.herokuapp.com/"

        # get the author and the follower
        current_author = self.get_object(author_id)

        if current_author.url_id == follower_id:
            return Response(status=status.HTTP_400_BAD_REQUEST) 

        # checks if follower already exists (to avoid duplicates)
        does_follower_exist = current_author.followers_items.filter(author_info__id = follower_id)
        
        if len(does_follower_exist) > 0: # this follower already exists
            return Response(status=status.HTTP_409_CONFLICT) 

        else: # follower does not exist
            host = follower_id.split('api/')[0]
            if host == our_host:
                local_follower = Author.objects.get(url_id = follower_id)
                serializer = AuthorSerializer(local_follower)
                author_dict = json.loads(json.dumps(serializer.data))
                current_author.followers_items.create(author_info = author_dict)
            else:
                headers = auth[host] # get authorization
                r = requests.get(follower_id, headers = headers)
                current_author.followers_items.create(author_info = r.json())
            return Response(status=status.HTTP_201_CREATED) 
    
class FollowingList(APIView):
    """
    URL: ://service/authors/{AUTHOR_ID}/following
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def check_for_remote_followers(self, author_object):
        authors_list = []
        following_remote_authors = []

        auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
        "https://sd7-api.herokuapp.com/": {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')}}

        r = requests.get("http://sd7-api.herokuapp.com/api/authors/", headers = {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')})
        authors_list.extend(r.json()["items"])

        r = requests.get("https://socialdistcmput404.herokuapp.com/api/authors/", headers = {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"})
        authors_list.extend(r.json()["items"])
  
        for author in authors_list:
            host = author["host"] + "/" if not author["host"].endswith("/") else author["host"]
            author_id = author["id"].split("/authors/")[-1]

            if "heroku" in host:
                r = requests.get(host + "api/authors/" + author_id + "/followers/" + author_object.url_id, headers = auth[host])
                if r.status_code == 200:
                    following_remote_authors.append(author)
                r.close()

        return following_remote_authors
        
    def get(self, request, author_id):
        """
        Get a list of authors that the current author is following (extra - not in spec, local)

        Returns a list of Author objects[{"type":"author"...},..] and a status code of 200 OK,
        else returns a status code of 404 Not Found
        """
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

        # get the "remote" followers
        following_remote_authors = self.check_for_remote_followers(current_author)
        following_list.extend(following_remote_authors)

        following_json = {"type": "following", "items": following_list}
        return Response(following_json)
    

class FriendsList(APIView):
    """
    URL: ://service/authors/{AUTHOR_ID}/friends
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def check_for_remote_followers(self, author_object):
            authors_list = []
            following_remote_authors = []

            auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
            "https://sd7-api.herokuapp.com/": {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')}}

            r = requests.get("http://sd7-api.herokuapp.com/api/authors/", headers = {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')})
            authors_list.extend(r.json()["items"])

            r = requests.get("https://socialdistcmput404.herokuapp.com/api/authors/", headers = {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"})
            authors_list.extend(r.json()["items"])
    
            for author in authors_list:
                host = author["host"] + "/" if not author["host"].endswith("/") else author["host"]
                author_id = author["id"].split("/authors/")[-1]

                if "heroku" in host:
                    r = requests.get(host + "api/authors/" + author_id + "/followers/" + author_object.url_id, headers = auth[host])
                    if r.status_code == 200:
                        following_remote_authors.append(author)
                    r.close()

            return following_remote_authors
    
    def get(self, request, author_id):
        '''
        Gets a list of the author's friends, where they follow each other (extra - not in spec, local)

        Returns a list of Author objects[{"type":"author"...},..] and a status code of 200 OK, 
        else, returns a status code of 404 Not Found
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

        # get the "remote" followers
        following_remote_authors = self.check_for_remote_followers(current_author)
        following_list.extend(following_remote_authors)

        follower_list = current_author.followers_items.all() # who is following them

        list_of_friends = []  

        for following in following_list: # for each author that the current author is following
            for follower in follower_list: # for each author that is following the current author

                following_id = following["id"]# id of the author who is being followed by the current author
                follower_id = follower.author_info["id"] 
                
                # this particular author is following the current author
                # and is being followed by the current author
                if following_id == follower_id: 
                    list_of_friends.append(following)


        friends_json = {"type": "friends", "items": list_of_friends}
        return Response(friends_json, status=status.HTTP_200_OK)
    