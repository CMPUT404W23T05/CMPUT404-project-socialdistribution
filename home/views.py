
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
import json
from urllib.parse import urlparse

class BrowsePosts(APIView, PageNumberPagination):
    def get(self, request, format=None):
        posts = Post.objects.filter(visibility='PUBLIC')

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', 20))

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostList(APIView, PageNumberPagination):
    def get(self, request, author_id, format=None):
        posts = Post.objects.filter(visibility='PUBLIC', author__author_id=author_id)

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', 20))

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)        

    @permission_classes([IsAuthenticated])
    def post(self, request, author_id, format=None):
        try:
            Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

        serializer = PostDeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    def get_object(self, post_id):
        try:
            return Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            raise Http404 

        # FOR RETRIEVING THE DETAILS OF A GIVEN POST
    def get(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

        # PUT DOES NOT WORK CURRENTLY - for creating a post from another node in db
    def put(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id)
        serializer = PostDeSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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

class ImageView(APIView):
    def get(self, request, author_id, post_id, format=None):
        post = Post.objects.get(post_id=post_id)
        image, content_type = post.get_image()

        if not image:
            raise Http404

        return HttpResponse(image, content_type=content_type)



class AuthorList(APIView, PageNumberPagination):
    def get(self, request, format=None):
        authors = Author.objects.all()

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', 20))

        results = self.paginate_queryset(authors, request, view=self)
        serializer = AuthorSerializer(results, many=True)
        response = {
                "type": "authors",
                "items": serializer.data
                }
        return Response(response, status=status.HTTP_200_OK)

class AuthorDetail(APIView):
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def get(self, request, author_id, format=None):
        author = self.get_object(author_id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
    def post(self, request, author_id, format=None):
        author = self.get_object(author_id)
        serializer = AuthorSerializer(instance=author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CommentList(APIView, PageNumberPagination):
    def get(self, request, post_id, author_id, format=None):
        comments = Comment.objects.filter(post_id=post_id)

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', 5))

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

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, post_id, author_id, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    def get_object(self, comment_id):
        try:
            return Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            raise Http404 

    def get(self, request, post_id, author_id, comment_id, format=None):
        comment = self.get_object(comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostLikes(APIView):
    """
    Get a list of likes from other authors on AUTHOR_ID’s post POST_ID

    Returns a status code of 200 OK, otherwise 404 Not Found if the author or the post
    does not exist
    """
    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
    
    def does_post_exist(self, post_id):
        try:
            Post.objects.get(post_id=post_id)
        except:
            raise Http404

    def get(self, author_id, post_id):

        # check if the author and post exist
        author = self.get_author_object(author_id=author_id)
        self.does_post_exist(post_id=post_id)

        filter_post_likes = Like.objects.filter(object=author.profile_url + "/posts/" + post_id)
        
        # turning the data into a list
        serializer = LikeSerializer(filter_post_likes, many=True)
        likes_data = json.dumps(serializer.data)
        likes_data_list = json.loads(likes_data)

        likes_json = {"type": "post_likes", "items": likes_data_list}
        return Response(likes_json, status=status.HTTP_200_OK)

class CommentLikes(APIView):
    """
    Get a list of likes from other authors on AUTHOR_ID’s post POST_ID comment COMMENT_ID

    Returns a status code of 200 OK, otherwise 404 Not Found if the author or the 
    comment does not exist
    """
    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def does_comment_exist(self, comment_id):
        try:
            Comment.objects.get(comment_id=comment_id)
        except:
            raise Http404

    def get(self, author_id, post_id, comment_id):
        
        # check if the author and the comment exists
        author = self.get_author_object(author_id=author_id)
        self.does_comment_exist(comment_id)

        # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}
        filter_comment_likes = Like.objects.filter(object=author.profile_url + "/posts/" + post_id + "/comments/" + comment_id)
        
        # turning the data into a list
        serializer = LikeSerializer(filter_comment_likes, many=True)
        likes_data = json.dumps(serializer.data)
        likes_data_list = json.loads(likes_data)

        likes_json = {"type": "comment_likes", "items": likes_data_list}
        return Response(likes_json, status=status.HTTP_200_OK)
    
class LikedList(APIView):
    """
    Get a list public things that the author AUTHOR_ID has liked
    """
    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        current_author = self.get_author_object(author_id)
        author_serializer = AuthorLikesSerializer(current_author)
        return Response(author_serializer.data, status=status.HTTP_200_OK)


class InboxDetails(APIView, PageNumberPagination):
    """
    Get the inbox of the author

    Returns a status code of 200 OK, otherwise returns a 404 Not Found if the author 
    does not exist
    """
    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id = author_id)
        except Author.DoesNotExist:
            raise Http404 

    @permission_classes([IsAuthenticated])
    def get(self, request, author_id):

        # get the current author and set up its id url
        current_author = self.get_author_object(author_id)

        inbox_items = Inbox.objects.filter(associated_author__author_id = author_id)

        # pagination
        self.page = int(request.query_params.get('page',1))
        self.page_size = int(request.query_params.get('size',20))
        inbox = self.paginate_queryset(inbox_items, request, view=self)

        serializer = InboxItemSerializer(inbox, many = True)
        inbox_data = json.dumps(serializer.data)
        inbox_list = json.loads(inbox_data)
        inbox_json = {"type": "inbox", "author": current_author.profile_url, "items": inbox_list}

        return Response(inbox_json, status=status.HTTP_200_OK)   
    
    def post(self, request, author_id):

        # get the current author and set up its id url
        current_author = self.get_object(author_id)

        # POST
        if request.data["type"] == "post":
            new_post = PostDeSerializer(data=request.data)
            new_post.is_valid()
            new_post.save()

            new_post_dict = json.loads(json.dumps(new_post.data))

            # checking that we're not adding duplicates in the inbox
            check_for_post = current_author.inbox_items.filter(inbox_item = new_post_dict)
            if len(check_for_post) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)  
            else:
                current_author.inbox_items.create(inbox_item = new_post_dict)
                return Response(new_post.data, status=status.HTTP_201_CREATED)  
        
        # COMMENT
        elif request.data["type"] == "comment":
            new_comment = CommentSerializer(data=request.data)
            new_comment.is_valid()

            new_comment.save()

            new_comment_dict = json.loads(json.dumps(new_comment.data))

            # checking that we're not adding duplicates in the inbox
            check_for_comment = current_author.inbox_items.filter(inbox_item = new_comment_dict)
            if len(check_for_comment) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)  
            else:
                current_author.inbox_items.create(inbox_item = new_comment_dict)
                return Response(new_comment.data, status=status.HTTP_201_CREATED)  

        # LIKE
        elif request.data["type"] == "Like":

            # checking that we're not adding duplicates in the inbox
            check_for_like = current_author.inbox_items.filter(inbox_item = request.data)
            if len(check_for_like) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)  
            else: # we haven't seen this like "post" before yet
                context_url = request.data["@context"] if "@context" in request.data.keys() else request.data["context"] 
                Like.objects.create_like(context_url, request.data["author"], request.data["object"])

                current_author.inbox_items.create(inbox_item = request.data)
                return Response(request.data, status=status.HTTP_201_CREATED)  

        # FOLLOW
        elif request.data["type"] == "Follow":
            does_follow_exist = Follow.objects.filter(author_object=request.data["object"]).filter(author_actor=request.data["actor"])

            # the follow does not exist (first time we're making a follow request)
            if len(does_follow_exist) == 0:
                new_follow = Follow.objects.create_follow(request.data["actor"], request.data["object"])
                serializer = FollowSerializer(new_follow)

                new_follow_data = json.loads(json.dumps(serializer.data))

                current_author.inbox_items.create(inbox_item = new_follow_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # updating the follow request (since it has been either accepted or declined)
            elif len(does_follow_exist) > 0 and "state" in request.data.keys(): # the follow request existed before, now it either got accepted or denied
                old_follow = does_follow_exist[0]
                serializer = FollowSerializer(old_follow)
                old_follow_data = json.loads(json.dumps(serializer.data)) # changing it to JSON dict

                # get the specific follow request from the inbox
                follow_from_inbox = current_author.inbox_items.filter(inbox_item = old_follow_data)[0]

                if request.data["state"] == "Accepted":

                    # create a follower
                    current_author.followers_items.create(author_info = json.loads(json.dumps(request.data["actor"])))

                    # earlier, had no state field, now has a state field of accepted
                    # (indicates that it has been handled)
                    follow_from_inbox.inbox_item["state"] = "Accepted"
                    does_follow_exist[0].state = "Accepted"

                    follow_from_inbox.save()
                    does_follow_exist[0].save(update_fields=["state"])

                    return Response(status=status.HTTP_200_OK)
                
                elif request.data["state"] == "Declined":
                    follow_from_inbox.inbox_item["state"] = "Declined"
                    does_follow_exist[0].state = "Declined"

                    follow_from_inbox.save()
                    does_follow_exist[0].save(update_fields=["state"])

                    return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
  
    def delete(self, request, author_id):

        # get the author and clear out the inbox
        current_author = self.get_object(author_id)

        all_items = current_author.inbox_items.all()
        all_items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
