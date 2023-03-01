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
