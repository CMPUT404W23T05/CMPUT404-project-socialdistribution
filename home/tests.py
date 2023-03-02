from django.test import TestCase, RequestFactory
from .models import Post, Author
from django.urls import reverse
from django.http import HttpResponse
import base64
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.base import ContentFile

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
                uid = "5c38b0da-f7bb-4fda-9cb1-852da4ab6ece",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Gandalf the Grey",
                profile_url = "http://127.0.0.1:5454/authors/5c38b0da-f7bb-4fda-9cb1-852da4ab6ece",
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
       # a2 = Author.objects.create(**self.author2)

        self.author.followers_items.create(**self.author2)
        a3 = Author.objects.create(**self.author3)

        request = self.factory.get("/authors/1/requests/")
       # response = requests_details(request, 1) # get the followers of author 1
      

# ---------------------- testing post model ----------------------------------
class PostTesting(TestCase):
    def setUp(self):
        # jpeg test image
        with open('home/test_image.jpeg', 'rb') as f:
            image_data = f.read()
            image_data_jpg = base64.b64encode(image_data)

        # png test image
        with open('home/test_image.png', 'rb') as f:
            image_data = f.read()
            image_data_png = base64.b64encode(image_data)

        # using json data as python dictionary
        self.author = Author.objects.create(
                object_type = "author",
                uid = "26dfb518-6dde-4ccb-bfbf-b95ba26d4e88",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Frodo Baggins",
                profile_url = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88",
                author_github = "http://github.com/frodobaggins",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )

        # valid author, png image
        self.post1 = Post.objects.create(
                object_type = "post",
                title = "example post 1",
                post_id = "decad856-d48d-4b2a-a100-b0734bcef0a7",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "This post is an example",
                content_type = "text/plain, image/png;base64",
                content = "testing... 1,2,3",
                image = ContentFile(base64.b64decode(image_data_png), name='test_image_1'),
                author = self.author,
                comment_count = 5,
                comments = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88/posts/decad856-d48d-4b2a-a100-b0734bcef0a7/comments",
                visibility = "PUBLIC",
                is_unlisted = False
                )

        # author exists, with image jpeg
        self.post2 = Post.objects.create(
                object_type = "post",
                title = "example post 2",
                post_id = "218049ef-ac5b-4f4c-a853-f8b8bd8dcd68",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "This post is an example",
                content_type = "text/plain, image/jpeg;base64",
                content = "testing... 1,2,3",
                image = ContentFile(base64.b64decode(image_data_jpg), name='test_image_2'),
                author = self.author,
                comment_count = 5,
                comments = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88/posts/218049ef-ac5b-4f4c-a853-f8b8bd8dcd68/comments",
                visibility = "PUBLIC",
                is_unlisted = False
                )

        # # not valid author id (doesn't exist)
        # self.post3 = Post.objects.create(
        #         object_type = "post",
        #         title = "example post 3",
        #         post_id = "6dc729f9-fb06-49a7-a23d-ccea129a24e8",
        #         post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
        #         post_origin = "http://whereitcamefrom.com/posts/zzzzz",
        #         description = "This post is an example",
        #         content_type = "text/plain, image/png;base64",
        #         content = "testing... 1,2,3",
        #         image = ContentFile(base64.b64decode(image_data_png), name='test_image_3'),
        #         author = Author.objects.get(uid="7b8bdf38-8231-46b4-a629-1951bcc62b9c"),
        #         comment_count = 5,
        #         comments = "http://127.0.0.1:5454/authors/7b8bdf38-8231-46b4-a629-1951bcc62b9c/posts/6dc729f9-fb06-49a7-a23d-ccea129a24e8/comments",
        #         visibility = "PUBLIC",
        #         is_unlisted = False
        #         )


    def test_post_model_is_valid_png(self):
        self.assertTrue(isinstance(self.post1, Post))

    def test_post_model_is_valid_jpg(self):
        self.assertTrue(isinstance(self.post2, Post))

    # def test_post_model_author_not_real(self):
    #     self.assertFalse(isinstance(self.post3, Post))

    def test_post_model_str(self):
        self.assertEqual(str(self.post1), "example post 1")
        self.assertEqual(str(self.post2), "example post 2")
        # self.assertNotEqual(str(self.post3), "example post 3")

 ############################## View Testing #############################3333

# class PostListViewTest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.author = User.objects.create
