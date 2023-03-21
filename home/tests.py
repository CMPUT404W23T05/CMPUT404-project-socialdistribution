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


# ---------------------- testing author model ----------------------------------
class AuthorTesting(TestCase):
    def setUp(self):
        self.user = User.objects.create(
                username = "Test1",
                password = "1234"
                )

        self.author = self.user.author

    def test_author_model_is_valid(self):
        d = self.author
        self.assertTrue(isinstance(d, Author))

    def test_author_model_str(self):
        d = self.author
        self.assertEqual(str(d), "Test1")


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

        self.user2 = User.objects.create(
                username = "Test2",
                password = "1234"
                )

        self.author2 = self.user2.author

        # valid author, png image
        self.post1 = Post.objects.create(
                object_type = "post",
                title = "example post 1",
                url_id = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88/posts/decad856-d48d-4b2a-a100-b0734bcef0a7",
                post_id = "decad856-d48d-4b2a-a100-b0734bcef0a7",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "This post is an example",
                content_type = "text/plain, image/png;base64",
                content = "testing... 1,2,3",
                image = ContentFile(base64.b64decode(image_data_png), name='test_image_1'),
                author = self.author2,
                comment_count = 5,
                comments = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88/posts/decad856-d48d-4b2a-a100-b0734bcef0a7/comments",
                visibility = "PUBLIC",
                is_unlisted = False
                )

        # author exists, with image jpeg
        self.post2 = Post.objects.create(
                object_type = "post",
                title = "example post 2",
                url_id = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88/posts/218049ef-ac5b-4f4c-a853-f8b8bd8dcd68",
                post_id = "218049ef-ac5b-4f4c-a853-f8b8bd8dcd68",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "This post is an example",
                content_type = "text/plain, image/jpeg;base64",
                content = "testing... 1,2,3",
                image = ContentFile(base64.b64decode(image_data_jpg), name='test_image_2'),
                author = self.author2,
                comment_count = 5,
                comments = "http://127.0.0.1:5454/authors/26dfb518-6dde-4ccb-bfbf-b95ba26d4e88/posts/218049ef-ac5b-4f4c-a853-f8b8bd8dcd68/comments",
                visibility = "PUBLIC",
                is_unlisted = False
                )


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

# ---------------------- testing follower model ----------------------------------
class FollowerTesting(TestCase):
    def setUp(self):
        
        self.author = Author.objects.create(
                object_type = "author",
                url_id = "http://127.0.0.1:5454/authors/a15eb467-5eb0-4b7d-9eaf-850c3bf7970c",
                author_id = "a15eb467-5eb0-4b7d-9eaf-850c3bf7970c",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Greg Johnson",
                profile_url = "http://127.0.0.1:5454/authors/a15eb467-5eb0-4b7d-9eaf-850c3bf7970c",
                author_github = "http://github.com/gjohnson",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )
        
        self.author2 = Author.objects.create(**{
                "object_type": "author",
                "url_id": "http://127.0.0.1:5454/authors/6dd28022-aaef-4bc7-af6f-9224ec6fcf42",
                "author_id": "6dd28022-aaef-4bc7-af6f-9224ec6fcf42",
                "home_host":  "http://127.0.0.1:5454/",
                "display_name": "Lara Croft",
                "profile_url": "http://127.0.0.1:5454/authors/6dd28022-aaef-4bc7-af6f-9224ec6fcf42",
                "author_github": "http://github.com/laracroft",
                "profile_image": "https://i.imgur.com/k7XVwpB.jpeg"
            })

        
        self.author3 = Author.objects.create(**{
                "object_type": "author",
                "url_id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658ee",
                "author_id": "4318ba4e-6f8d-4f3e-985a-ea2fadb7cd87",
                "home_host":  "http://127.0.0.1:5454/",
                "display_name": "John Doe",
                "profile_url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658ee",
                "author_github": "http://github.com/jdoe",
                "profile_image": "https://i.imgur.com/k7XVwpB.jpeg"
            })
        

    def test_followers_get(self):
        serializer = AuthorSerializer(self.author2)
        author_data = json.dumps(serializer.data)
        author_data_dict = json.loads(author_data)
        
        self.author.followers_items.create(author_info = author_data_dict)
        self.assertEqual(len(self.author.followers_items.all()), 1)

    def test_follow_manager(self):
        author_serializer = AuthorSerializer(self.author)
        author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(author_data)
        
        author2_serializer = AuthorSerializer(self.author2)
        author2_data = json.dumps(author2_serializer.data)
        author2_data_dict = json.loads(author2_data)
        

        test_follow = Follow.objects.create_follow(author_data_dict, author2_data_dict)
        follow = FollowSerializer(test_follow)
        
        self.assertEqual(len(Follow.objects.all()), 1)

    def test_likes(self):
        context = "https://www.w3.org/ns/activitystreams"
        object_link = "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e"

        serializer = AuthorSerializer(self.author)
        author_dict = json.loads(json.dumps(serializer.data))

        Like.objects.create_like(context, author_dict, object_link)
        self.assertTrue(len(Like.objects.all()), 1)
        


 ############################## View Testing #############################3333

# class PostListViewTest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.author = User.objects.create
