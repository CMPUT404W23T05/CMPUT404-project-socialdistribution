
from django.test import TestCase, RequestFactory
from .models import Post, Author
from django.urls import reverse
from django.http import HttpResponse
import base64
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.base import ContentFile

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json
from rest_framework.renderers import JSONRenderer
from .views import *
import uuid
import requests


class InboxTesting(TestCase):
    def setUp(self):
        # for the sake of testing, assume that http://127.0.0.1:8000/ is the remote author
        # and https://social-t30.herokuapp.com/ is the local author

        # our "remote" author
        self.author = Author.objects.create(
                object_type = "author",
                url_id = "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea",
                author_id = "d569cd39-0a2d-411e-8d86-e8a063a18dea",
                home_host = "http://127.0.0.1:8000/",
                display_name = "testuser1",
                profile_url = "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea",
                author_github = "",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )
        
        # our "local author"
        self.author2 = Author.objects.create(**{
                "object_type": "author",
                "url_id": "http://127.0.0.1:8000/api/authors/38f57b34-f1ff-4f3b-9e81-2be731a14a0e",
                "author_id": "38f57b34-f1ff-4f3b-9e81-2be731a14a0e",
                "home_host":  "https://social-t30.herokuapp.com/",
                "display_name": "testuser2",
                "profile_url": "https://social-t30.herokuapp.com/api/authors/38f57b34-f1ff-4f3b-9e81-2be731a14a0e",
                "author_github": "",
                "profile_image": "https://i.imgur.com/k7XVwpB.jpeg"
            })
        
        # author 1 (our "remote" author) will create this post
        self.post = Post.objects.create(
                object_type = "post",
                title = "Today is Tuesday",
                url_id = "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b",
                post_id = "d091e3f1-4482-4d9d-8673-ac913f44fb9b",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "This post is an example",
                content_type = "text/plain, image/png;base64",
                content = "testing... 1,2,3",
                author = self.author,
                comment_count = 0,
                comments = "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b/comments",
                visibility = "PUBLIC",
                is_unlisted = False
                )
        # author 2 (our "local" author) will create this post
        self.post2 = Post.objects.create(
                object_type = "post",
                title = "Today is Wednesday",
                url_id = "https://social-t30.herokuapp.com/api/authors/38f57b34-f1ff-4f3b-9e81-2be731a14a0e/posts/decad856-d48d-4b2a-a100-b0734bcef0a7",
                post_id = "decad856-d48d-4b2a-a100-b0734bcef0a7",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "This post is an example",
                content_type = "text/plain, image/png;base64",
                content = "testing... 1,2,3",
                author = self.author2,
                comment_count = 0,
                comments = "https://social-t30.herokuapp.com/api/authors/38f57b34-f1ff-4f3b-9e81-2be731a14a0e/posts/decad856-d48d-4b2a-a100-b0734bcef0a7/comments",
                visibility = "PUBLIC",
                is_unlisted = False
                )
        # author 2 (our "local" author) leave a comment on the remote author's post
        self.comment_for_author_1 = Comment.objects.create(
                object_type = "comment",
                url_id = "https://social-t30.herokuapp.com/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b/comments/73fe120d-1f19-44e4-9a7f-c184b7df5597",
                comment_id = "73fe120d-1f19-44e4-9a7f-c184b7df5597",
                post_id =  "d091e3f1-4482-4d9d-8673-ac913f44fb9b",
                author = self.author2,
                content = "I am author 2!",
                content_type = "text/plain"
                )

    def test_send_post_to_remote_follower_inbox(self):
        # add author 1 (our "remote" author) as a follower of author 2
        serializer = AuthorSerializer(self.author)
        author_data = json.dumps(serializer.data)
        author_data_dict = json.loads(author_data)
        self.author2.followers_items.create(author_info = author_data_dict)
        self.assertEqual(len(self.author2.followers_items.all()), 1)

        post = Post.objects.get(url_id=self.post2.url_id)
        post_serializer = PostSerializer(post)
        followers_serializer = AuthorFollowersSerializer(post.author) # get the followers
        for item in followers_serializer.data['items']:
            follower_host = item["host"] + "/" if not item["host"].endswith("/") else item["host"]
 
            if follower_host != self.author2.home_host: # if it's a remote author
                follower_id = item["id"].split("/")[-1]
                url = follower_host + "api/authors/" + follower_id + "/inbox/" 
                r = requests.head(url) 
                self.assertEqual(r.status_code, 200) # check if url exists


    def test_send_comment_to_remote_author_inbox(self):
        is_local_post = len(Post.objects.filter(url_id=self.comment_for_author_1.url_id)) # get the post based on its url
        comment = Comment.objects.get(url_id=self.comment_for_author_1.url_id) # get the comment based on its id
        comment_serializer = CommentSerializer(comment)
        if not is_local_post: # a local author commented on a remote post
            comment_url = comment.url_id
            get_remote_author_info = comment_url.split('posts/')[0]
            url = get_remote_author_info + '/inbox/'
            r = requests.head(url) 
            self.assertEqual(r.status_code, 200) # check if url exists

