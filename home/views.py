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


class BrowsePosts(APIView, PageNumberPagination):
    '''
    URL: ://service/api/posts/
    '''
    def get(self, request, format=None):
        posts = Post.objects.filter(visibility='PUBLIC')

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', 20))

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostList(APIView, PageNumberPagination):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/posts/
    '''
    def get(self, request, author_id, format=None):
        posts = Post.objects.filter(visibility='PUBLIC', author__uid=author_id)

        self.page = int(request.query_params.get('page', 1))
        self.page_size = int(request.query_params.get('size', 20))

        results = self.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)        

    @permission_classes([IsAuthenticated])
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


class PostDetail(APIView):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/
    '''
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

class FollowersList(APIView):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/followers
    '''
    def get(self, request, author_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0] # get the first match
            serializer = AuthorFollowersSerializer(current_author) # get all the followers
        except:
            return Response(status=status.HTTP_404_NOT_FOUND) # author id does not exist
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    
class FollowersDetails(APIView):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
    '''
    def get(self, request, author_id, follower_id):
        try:
            # get the first match
            current_author = Author.objects.filter(uid=author_id)[0]
            selected_follower = Author.objects.filter(uid=follower_id)[0]

            serializer = AuthorSerializer(selected_follower)
            json_info = JSONRenderer().render(serializer.data)
            follower_info = json_info.decode("utf-8")
        
            # is this author a follower of the current author? Compare the information
            check_follower = current_author.followers_items.filter(author_info = follower_info)[0]
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_200_OK)
        
    def delete(self, request, author_id, follower_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
            selected_follower = Author.objects.filter(uid=follower_id)[0]
            
            serializer = AuthorSerializer(selected_follower)
            json_info = JSONRenderer().render(serializer.data)
            follower_info = json_info.decode("utf-8")
        
            selected_follower = current_author.followers_items.filter(author_info = follower_info)[0]
        
        except: 
            return Response(status=status.HTTP_404_NOT_FOUND)  
        else:
            selected_follower.delete() 
            return Response(status=status.HTTP_204_NO_CONTENT) 

    def put(self, request, author_id, follower_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
            selected_follower = Author.objects.filter(uid=follower_id)[0]
            
            serializer = AuthorSerializer(selected_follower)
            json_info = JSONRenderer().render(serializer.data)
            follower_info = json_info.decode("utf-8")
        
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)  
        else:
            current_author.followers_items.create(author_info = follower_info)
            return Response(status=status.HTTP_201_CREATED) 
    
class FollowingList(APIView):
    """
    Get a list of authors that the current author is following

    Returns a list [{"type":"author"...},..]
    """
    def get(self, request, author_id):
        try:
            current_author = Author.objects.filter(uid=author_id)[0]
        
            serializer = AuthorSerializer(current_author)
            json_info = JSONRenderer().render(serializer.data)
            current_author_info = json_info.decode("utf-8")

            # check if the author is the followers_list of the authors
            following_authors = Author.objects.filter(followers_items__author_info = current_author_info)
        except:
            raise Http404
        else:
            serializer = AuthorSerializer(following_authors, many=True)
            return Response(serializer.data)

class FriendsList(APIView):
    """
    Gets all the friends of the author (they each accepted each other's follow request)

    Returns a list [{"type":"author"...},..]
    """
    def get(self, request, author_id):

        current_author = Author.objects.filter(uid=author_id)[0]

        serializer = AuthorSerializer(current_author)
        json_info = JSONRenderer().render(serializer.data)
        current_author_info = json_info.decode("utf-8")

        following_list = Author.objects.filter(followers_items__author_info= current_author_info) 
        follower_list = current_author.followers_items.all() # who is following them
        list_of_friends = []  

        for following in following_list:
            for follower in follower_list:
                following_id = following.profile_url # id of the author who is being followed by the current author
                follower_id = (json.loads(follower.author_info))['url']
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


class ImageView(APIView):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/image
    '''

    def get(self, request, author_id, post_id, format=None):
        post = Post.objects.get(post_id=post_id)
        image, content_type = post.get_image()

        if not image:
            raise Http404

        return HttpResponse(image, content_type=content_type)



class AuthorList(APIView, PageNumberPagination):
    '''
    URL: ://service/api/authors/
    '''

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
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/
    '''

    def get_object(self, author_id):
        try:
            return Author.objects.get(uid=author_id)
        except Author.DoesNotExist:
            raise Http404 

    def get(self, request, author_id, format=None):
        author = self.get_object(author_id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, author_id, format=None):
        author = self.get_object(author_id)
        serializer = AuthorSerializer(instance=author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CommentList(APIView, PageNumberPagination):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/comments
    '''

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

    # @permission_classes([IsAuthenticated])
    def post(self, request, post_id, author_id, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    '''
    URL: ://service/api/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}
    '''

    def get_object(self, comment_id):
        try:
            return Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            raise Http404 

    def get(self, request, post_id, author_id, comment_id, format=None):
        comment = self.get_object(comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)


