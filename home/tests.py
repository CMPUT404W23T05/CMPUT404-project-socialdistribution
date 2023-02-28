from django.test import TestCase, RequestFactory
from .models import Post, Author
from datetime import datetime
from django.urls import reverse

from .views import *
import json 

# ---------------------- testing post model ----------------------------------
class PostTesting(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
                object_type = "post",
                title = "example post",
                post_id = "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd3/posts/764efa883dda1e11db4767",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "this is an example post for testing",
                content_type = "text/plain",
                content = "testing... 1,2,3",
                # author = {},
                # categories = [] # this is where we put tags as list of strs
                comment_count = 5,
                comments = "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34/posts/764efa8e3dd81e11db4941/comments",
                # commentsSrc = "put here"  # OPTIONAL, for reducing api calls later
                pub_date = "2015-03-09T13:07:04+00:00",
                visibility = "PUBLIC",
                is_unlisted = False
                )

    def test_post_model_is_valid(self):
        d = self.post
        self.assertTrue(isinstance(d, Post))

    def test_post_model_str(self):
        d = self.post
        self.assertEqual(str(d), "example post")


class PlainTextPostTesting(TestCase):
    def setUp(self):
        # data for test_post_creation()
        self.post_data = {
                "type": "post",
                "title": "Test Plain Text Post",
                "contentType": "text/plain",
                "content": "testing...123"
                }

        self.post_data1 = {
                "type": "post",
                "contentType": "text/plain",
                "content": "testing...123"
                }

        self.post_data2 = {
                "type": "post",
                "title": "Test Plain Text Post",
                "contentType": "text/plain",
                "content": "testing...123"
                }

        self.post_data3 = {
                "type": "post",
                "title": "Test Plain Text Post",
                "contentType": "text/plain",
                "content": "testing...123"
                }

    def test_post_creation(self):
        url = reverse("index")
        response = self.client.post(url, self.post_data)
        self.assertEqual(response.status_code, 200)
        pid = "http://127.0.0.1:5454/authors/2/posts/2"

        try:
            post = Post.objects.get(post_id = pid)
        except Post.DoesNotExist:
            post = None

        self.assertIsNotNone(post)
        self.assertEqual(post.object_type, "post")
        self.assertEqual(post.title, "Test Plain Text Post")
        self.assertEqual(post.content_type, "text/plain")
        self.assertEqual(post.content, "testing...123")
        self.assertEqual(post.post_source, "https://www.example.com/source")
        self.assertEqual(post.post_origin, "https://www.example.com/origin")
        self.assertEqual(post.comments, "http://127.0.0.1:5454/authors/2/posts/2/comments") # placeholder
        self.assertEqual(post.comment_count, 0) # placeholder
        self.assertEqual(post.is_unlisted, False)
        self.assertEqual(post.visibility, "PUBLIC")
        # replace this later with a check on the actual datetime


    # def test_missing_title(self):


# ---------------------- testing author model ----------------------------------
class AuthorTesting(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
                object_type = "author",
                uid = "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Gandalf the Grey",
                profile_url = "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                author_github = "http://github.com/gandalfthegrey",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )

    def test_author_model_is_valid(self):
        d = self.author
        self.assertTrue(isinstance(d, Author))

    def test_author_model_str(self):
        d = self.author
        self.assertEqual(str(d), "Gandalf the Grey")

# ---------------------- testing follower model ----------------------------------
class FollowerTesting(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.author = Author.objects.create(
                object_type = "author",
                uid = "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f58147",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Greg Johnson",
                profile_url = "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                author_github = "http://github.com/gjohnson",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )
        
        self.author2 = {
                "object_type": "author",
                "uid": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "home_host":  "http://127.0.0.1:5454/",
                "display_name": "Lara Croft",
                "profile_url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "author_github": "http://github.com/laracroft",
                "profile_image": "https://i.imgur.com/k7XVwpB.jpeg"
            }
        
        
        self.author3 = {
                "object_type": "author",
                "uid": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658ee",
                "home_host":  "http://127.0.0.1:5454/",
                "display_name": "John Doe",
                "profile_url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658ee",
                "author_github": "http://github.com/jdoe",
                "profile_image": "https://i.imgur.com/k7XVwpB.jpeg"
            }
        
        
    def test_followers_get(self):
        self.author.followers_items.create(**self.author2)
        Author.objects.create(**self.author3)

        request = self.factory.get("/authors/1/followers/")
        response = followers(request, 1) # get the followers of author 1
      
