
from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import permission_classes
from django.http import HttpResponse, Http404
from djoser.views import TokenCreateView
from home.permissions import RemoteAuth, CustomIsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import sys



class RemoteApiKey(APIView):
    """
    URL: ://service/api/remotes/{URL}
    """
    permission_classes = [AllowAny]
        
    def get(self, request, url, format=None):
        try:
            remote = Remote.objects.get(url=url)
        except Remote.DoesNotExist:
            raise Http404

        serializer = RemoteSerializer(remote)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenericKey(APIView):
    """
    URL: ://service/api/key
    """
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        try:
            user = User.objects.get(username='anonymous')
            try:
                token_obj = Token.objects.get(user=user)
                token = token_obj.key
            except Token.DoesNotExist:
                raise Http404
        except User.DoesNotExist:
            Http404
        response = {"api_key": token}
        return Response(response, status=status.HTTP_200_OK)
 

class BrowsePosts(APIView, PageNumberPagination):
    """
    URL: ://service/api/posts/
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]

    def get(self, request, format=None):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        posts = Post.objects.filter(visibility='PUBLIC')

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', len(posts)))

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        response_body = {
                    'type': 'posts',
                    'items': serializer.data
                   }
        return Response(response_body, status=status.HTTP_200_OK)


class PostList(APIView, PageNumberPagination):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/posts/
    
    GETs can have param, type, that can be PUBLIC or FRIENDS for filtering which type
    of Posts are returned.
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def get(self, request, author_id, format=None):
        author = self.get_object(author_id)
        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)
        followers_serializer = AuthorFollowersSerializer(author)

        # checks if logged in user is the author in the url or a friend/follower of the author in the url
        if uid and ((str(uid) == str(author_id)) or (any(item['_id'] == str(uid) for item in followers_serializer.data['items']))):
            visibility = request.query_params.get('type', None)
            if visibility:
                posts = Post.objects.filter(visibility=visibility, author__author_id=author_id)
            else:
                posts = Post.objects.filter(author__author_id=author_id)
        else:
            posts = Post.objects.filter(visibility='PUBLIC', author__author_id=author_id)


        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', len(posts)))

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def post(self, request, author_id, format=None):
        author = self.get_object(author_id)
        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)

        if uid and (str(uid) == str(author_id)):
            serializer = PostDeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


       
class PostDetail(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]


    def get_object(self, post_id, author_id):
        try:
            return Post.objects.get(post_id=post_id, author__author_id=author_id)
        except Post.DoesNotExist:
            raise Http404 

    def get_author(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404

        # FOR RETRIEVING THE DETAILS OF A GIVEN POST
    def get(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id, author_id)
        author = self.get_author(author_id)
        if post.visibility == 'PUBLIC':
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)

        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)
        followers_serializer = AuthorFollowersSerializer(author)

        if uid and (str(uid) == str(author_id)):
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        for item in followers_serializer.data['items']:
            if item['_id'] == str(uid) and uid:
                serializer = PostSerializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        # PUT DOES NOT WORK CURRENTLY - for creating a post from another node in db
    @permission_classes([IsAuthenticated])
    def put(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id, author_id)
        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)
        
        if uid and (str(uid) == str(author_id)):
            serializer = PostDeSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # FOR EDITING EXISTING POST
    def post(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id, author_id)
        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)

        if uid and (str(uid) == str(author_id)):
            serializer = PostDeSerializer(instance=post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


        # FOR DELETING EXISITING POST
    def delete(self, request, post_id, author_id, format=None):
        post = self.get_object(post_id, author_id)
        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)

        if uid and (str(uid) == str(author_id)):
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class ImageView(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/image
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_object(self, post_id, author_id):
        try:
            return Post.objects.get(post_id=post_id, author__author_id=author_id)
        except Post.DoesNotExist:
            raise Http404

    def get_author(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404


    def get(self, request, author_id, post_id, format=None):
        post = self.get_object(post_id, author_id)
        author = self.get_author(author_id)
        image, content_type = post.get_image()
        if not image:
            raise Http404
        response = HttpResponse(image, content_type=content_type)

        if post.visibility == 'PUBLIC':
            return response

        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)
        followers_serializer = AuthorFollowersSerializer(author)

        if uid and (str(uid) == str(author_id)):
            return response
        for item in followers_serializer.data['items']:
            if item['_id'] == str(uid) and uid:
                return response
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



class AuthorList(APIView, PageNumberPagination):
    """
    URL: ://service/api/authors/
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]


    def get(self, request, format=None):
        authors = Author.objects.all()

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', len(authors)))

        results = self.paginate_queryset(authors, request, view=self)
        serializer = AuthorSerializer(results, many=True)
        response = {
                "type": "authors",
                "items": serializer.data
                }
        return Response(response, status=status.HTTP_200_OK)

class AuthorDetail(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]    

    def get_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def get(self, request, author_id, format=None):
        author = self.get_object(author_id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, author_id, format=None):
        author = self.get_object(author_id)
        uid = getattr(getattr(request.user, 'author', None), 'author_id', None)
        if uid and (str(uid) == str(author_id)):
            serializer = AuthorSerializer(instance=author, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



class CommentList(APIView, PageNumberPagination):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/comments
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_object(self, post_id, author_id):
        try:
            return Post.objects.get(post_id=post_id, author__author_id=author_id)
        except Post.DoesNotExist:
            raise Http404
            
    def get_author(self, author_id):
        try:
            Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def get(self, request, post_id, author_id, format=None):
        self.get_author(author_id)
        post = self.get_object(post_id, author_id)
        comments = Comment.objects.filter(post_id=post_id)

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', len(comments)))

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
        self.get_object(post_id, author_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    """
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_object(self, post_id, author_id):
        try:
            return Post.objects.get(post_id=post_id, author__author_id=author_id)
        except Post.DoesNotExist:
            raise Http404

    def get_comment(self, comment_id):
        try:
            return Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            raise Http404 
                                 
    def get_author(self, author_id):
        try:
            Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def get(self, request, post_id, author_id, comment_id, format=None):
        post = self.get_object(post_id, author_id)
        self.get_author(author_id)
        comment = self.get_comment(comment_id)

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PostLikes(APIView):
    """
    Get a list of likes from other authors on AUTHOR_ID’s post POST_ID

    Returns a status code of 200 OK, otherwise 404 Not Found if the author or the post
    does not exist
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
    
    def does_post_exist(self, author_id, post_id):
        try:
            post = Post.objects.get(post_id=post_id, author__author_id=author_id)
        except:
            raise Http404

    def get(self, request, author_id, post_id):

        # check if the author and post exist
        self.does_post_exist(author_id, post_id)
        author = self.get_author_object(author_id)
        
        object_url = author.profile_url + "/posts/" + str(post_id) 
        filter_post_likes = Like.objects.filter(obj=object_url)
  
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

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def get_object(self, author_id, post_id):
        try:
            return Post.objects.get(author__author_id=author_id, post_id = post_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def does_comment_exist(self, author_id, comment_id):
        try:
            comment = Comment.objects.get(comment_id = comment_id)
        except:
            raise Http404


    def get(self, request, author_id, post_id, comment_id):
        
        # check if the author, post and the comment exists
        author = self.get_object(author_id)
        self.does_comment_exist(author_id, comment_id)

        # URL: ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}
        object_url = author.profile_url + "/posts/" + str(post_id) + "/comments/" + str(comment_id)
        filter_comment_likes = Like.objects.filter(obj=object_url)

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
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get(self, request, author_id):
        current_author = self.get_author_object(author_id)
        author_serializer = AuthorPublicLikesSerializer(current_author)
        return Response(author_serializer.data, status=status.HTTP_200_OK)



@method_decorator(csrf_exempt, name='post')
class InboxDetails(APIView, PageNumberPagination):
    """
    Get the inbox of the author

    Returns a status code of 200 OK, otherwise returns a 404 Not Found if the author 
    does not exist
    """
    
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id = author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def handle_local_or_remote_post(self, request):
        """
        1. local to local inbox (public/friends posts): handled through signals.py
        2. local to remote inbox (public/friends posts): handled through signals.py
        4. remote to local inbox (public/friends posts): handled through InboxDetails
        """

        url_id = request.data['id'] # get the url
        is_local_post = len(Post.objects.filter(url_id=url_id))
        
        if not is_local_post: # if it is a remote post, leave it unchanged and put in inbox
            new_post_dict = request.data
        else: # if it's a local post, get the data from post objects and change to our format
            access_post = Post.objects.get(url_id=url_id)
            serializer = PostSerializer(access_post)
            new_post_dict = json.loads(json.dumps(serializer.data))
            
        return new_post_dict
    
    def handle_remote_follow_request(self, request):
        # given the object and actor that are url strings, do some modifications

        actor_url = request.data["author"] if isinstance(request.data["author"], str) else request.data["author"]["id"]
        object_url = request.data["object"] if isinstance(request.data["object"], str) else request.data["object"]["id"]
        remote_auth = {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')}

        # get information about our own author
        object_id = object_url.split("/")[-1] 
        object = Author.objects.get(author_id = uuid.UUID(object_id))
        object_serializer = AuthorSerializer(object)

        #r = requests.get(actor_url, headers = remote_auth)
        #actor = r.json()

        follow_format = {"type": "Follow",
                         "actor": actor_url,
                        "object": object_serializer.data,
                        "summary": actor_url + " wants to follow " + object_serializer.data["displayName"]}

        return follow_format 
    
    def handle_local_or_remote_comment(self, request):
        """
        1. local to local comment: handled through signals.py
        2. remote to local comment: handled through InboxDetails 
        """
        # for some groups, it may be left blank (and will throw an error)
        if request.data['author']['profileImage'] == "":
            default_profile_pic = "https://cdn.dribbble.com/users/6142/screenshots/5679189/media/1b96ad1f07feee81fa83c877a1e350ce.png?compress=1&resize=1200x900&vertical=top"
            request.data['author']['profileImage'] = default_profile_pic

        new_comment = CommentSerializer(data=request.data)

        author_url = request.data["author"]["id"]
        author_id = request.data["author"]["id"].split("/")[-1] 
        comment = request.data['comment']
        is_local_comment = Comment.objects.filter(url_id=request.data['id'])

        if new_comment.is_valid():
            if not is_local_comment: # if it's a remote comment
                does_author_exist = len(Author.objects.filter(author_id=author_id))

                # associate the comment with an author (also helps to keep track of comment count)
                Author.objects.create(**new_comment.validated_data['author']) if not does_author_exist else False
                new_comment.validated_data['author'] = Author.objects.get(url_id = author_url)
                access_comment = Comment.objects.create(**new_comment.validated_data)

                serializer = CommentSerializer(access_comment)
                new_comment_dict = json.loads(json.dumps(serializer.data))

            else:
                # a local author has created a new comment, we can retrieve that comment
                access_comment = Comment.objects.get(content = comment, author__url_id = author_url)

                serializer = CommentSerializer(access_comment)
                new_comment_dict = json.loads(json.dumps(serializer.data))

        else: # comment data is not valid, return its errors
            return {"details": new_comment.errors}

        return new_comment_dict
    
    def get(self, request, author_id):

        # get the current author and set up its id url
        current_author = self.get_author_object(author_id)

        inbox_items = Inbox.objects.filter(associated_author__author_id = author_id)
      
        # pagination
        self.page = int(request.query_params.get('page',1))
        self.page_size = int(request.query_params.get('size',len(inbox_items)))
        inbox = self.paginate_queryset(inbox_items, request, view=self)
       
        serializer = InboxItemSerializer(inbox, many = True)
        inbox_data = json.dumps(serializer.data)
        inbox_list = json.loads(inbox_data)
   
        inbox_json = {"type": "inbox", "author": current_author.profile_url, "items": inbox_list}

        return Response(inbox_json, status=status.HTTP_200_OK)   
    
    def post(self, request, author_id):
        # get the current author 
        current_author = self.get_author_object(author_id)

        print(request.data)
        sys.stdout.flush()

        # POST
        if request.data["type"] == "post":

            new_post_dict = self.handle_local_or_remote_post(request)
 
            # checking that we're not adding duplicates in the inbox
            check_for_post = current_author.inbox_items.filter(inbox_item = new_post_dict)
            if len(check_for_post) > 0:
                return Response({"detail": "This post already exists in their inbox"}, status=status.HTTP_409_CONFLICT)  
            else:
                current_author.inbox_items.create(inbox_item = new_post_dict)
                return Response(status=status.HTTP_201_CREATED)  
        
        # COMMENT
        elif request.data["type"] == "comment":

            if "private" not in request.data.keys(): # if it's a public comment, take appropiate action
                new_comment_dict = self.handle_local_or_remote_comment(request)
            else:
                new_comment_dict = request.data # private comment

            # return the error details back to them if it's a bad request
            if "details" in new_comment_dict:
                return Response(new_comment_dict, status=status.HTTP_400_BAD_REQUEST)  

            # checking that we're not adding duplicates in the inbox
            check_for_comment = current_author.inbox_items.filter(inbox_item = new_comment_dict)
            if len(check_for_comment) > 0:
                return Response({"detail": "This post already exists in their inbox"}, status=status.HTTP_409_CONFLICT)  
            else:
                current_author.inbox_items.create(inbox_item = new_comment_dict)
                return Response(status=status.HTTP_201_CREATED)  

        # LIKE
        elif request.data["type"] == "Like":

            # checking that we're not adding duplicates in the inbox
            check_for_like = current_author.inbox_items.filter(inbox_item = request.data)
            if len(check_for_like) > 0:
                return Response({"detail": "This post already exists in their inbox"}, status=status.HTTP_409_CONFLICT)  
            else: # we haven't seen this like "post" before yet
                try:
                    context_url = request.data["@context"] if "@context" in request.data.keys() else request.data["context"] 
                    Like.objects.create_like(context_url, request.data["author"], request.data["object"])
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)  
                else:
                    current_author.inbox_items.create(inbox_item = request.data)
                    return Response(status=status.HTTP_201_CREATED)  

        # FOLLOW
        elif request.data["type"] == "Follow" or request.data["type"] == "follow":
            
            if "author" in request.data.keys(): # got a request from team 7
                follow_format = self.handle_remote_follow_request(request)
            else:
                follow_format = request.data

            author_object_id = follow_format["object"]["id"]
            author_actor_id = follow_format["actor"]["id"]
            does_follow_exist = Follow.objects.filter(author_object__id=author_object_id).filter(author_actor__id=author_actor_id)
      
            # the follow does not exist (first time we're making a follow request)
            if len(does_follow_exist) == 0:
                new_follow = Follow.objects.create_follow(follow_format["actor"], follow_format["object"])
                serializer = FollowSerializer(new_follow)

                new_follow_data = json.loads(json.dumps(serializer.data))

                current_author.inbox_items.create(inbox_item = new_follow_data)
                return Response(status=status.HTTP_201_CREATED)

            # updating the follow request (since it has been either accepted or declined)
            elif len(does_follow_exist) > 0 and "state" in request.data.keys(): # the follow request existed before, now it either got accepted or denied

                if request.data["state"] == "Accepted":

                    # create a follower
                    current_author.followers_items.create(author_info = follow_format["actor"])

                    # earlier, had no state field, now has a state field of accepted
                    # (indicates that it has been handled)
                    does_follow_exist[0].state = "Accepted"
                    serializer = FollowStateSerializer(does_follow_exist[0])
                    old_follow_data = json.loads(json.dumps(serializer.data)) # changing it to JSON dict
                    current_author.inbox_items.create(inbox_item = old_follow_data)

                    does_follow_exist[0].save(update_fields=["state"])

                    return Response(status=status.HTTP_200_OK)
                
                elif request.data["state"] == "Declined":

                    does_follow_exist[0].state = "Declined"
                    serializer = FollowStateSerializer(does_follow_exist[0])
                    old_follow_data = json.loads(json.dumps(serializer.data)) # changing it to JSON dict
                    current_author.inbox_items.create(inbox_item = old_follow_data)


                    does_follow_exist[0].save(update_fields=["state"])

                    return Response(status=status.HTTP_200_OK)
                
            else:
                return Response({"detail": "This post already exists in their inbox"}, status=status.HTTP_409_CONFLICT)
                    
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
  
    def delete(self, request, author_id):

        # get the author and clear out the inbox
        current_author = self.get_author_object(author_id)

        all_items = current_author.inbox_items.all()
        all_items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@method_decorator(csrf_exempt, name='post')
class RedirectToInbox(APIView, PageNumberPagination):

    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def post(self, request, author_id):
        return InboxDetails().post(request, author_id)
    
class RemoteRequestsList(APIView, PageNumberPagination):
    """
    Keeps track of what remote follow requests that the author has sent (local to remote requests)
    """

    def get_author_object(self, author_id):
        try:
            return Author.objects.get(author_id = author_id)
        except Author.DoesNotExist:
            raise Http404 
        
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [RemoteAuth | CustomIsAuthenticated]
        elif self.request.method == 'OPTIONS':
            permission_classes = [AllowAny]
        else:
            permission_classes = [CustomIsAuthenticated]

        return [permission() for permission in permission_classes]

    def get(self, request, author_id):
        current_author = self.get_author_object(author_id)
        remote_requests = RemoteFollow.objects.filter(author_id = author_id)
        remote_requests_serializer = RemoteFollowSerializer(remote_requests, many=True)

        remote_json = {"type": "remote_requests", "items": remote_requests_serializer.data}
        return Response(remote_json, status=status.HTTP_200_OK)

    def put(self, request, author_id):
        current_author = self.get_author_object(author_id)
        
        # to-do: put into serializer later and remove from here
        required_keys = ["type", "actor", "object"]
        required_author_keys = ["type", "id", "host", "displayName", "github", "profileImage"]
        check_authors = set(required_author_keys) <= request.data["actor"].keys() and set(required_author_keys) <= request.data["object"].keys()
        if (set(required_keys) <= request.data.keys() and check_authors):
            RemoteFollow.objects.create(remote_follow_info = request.data, author_id = author_id)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You may be missing a field somewhere in your follow request"}, status=status.HTTP_400_BAD_REQUEST)
        
