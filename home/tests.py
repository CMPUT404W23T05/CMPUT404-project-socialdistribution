from django.test import TestCase, RequestFactory
from .models import Post, Author
from django.urls import reverse
from django.http import HttpResponse
import base64
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.base import ContentFile


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

 ############################## View Testing #############################3333

# class PostListViewTest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.author = User.objects.create
