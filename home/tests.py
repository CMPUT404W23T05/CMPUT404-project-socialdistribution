from django.test import TestCase
from .models import Post, Author
from django.urls import reverse
from django.http import HttpResponse
import base64


# ---------------------- testing author model ----------------------------------
class AuthorTesting(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
                object_type = "author",
                uid = "9de17f29c12e8f97bcbbd34cc908f1baba40658e",
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


# ---------------------- testing post model ----------------------------------
class PostTesting(TestCase):
    def setUp(self):
        # jpeg test image
        with open('home/test_image.jpeg', 'rb') as f:
            image_data = f.read()
            image_data = base64.b64encode(image_data)

        # png test image
        with open('home/test_image.png', 'rb') as f:
            image_data2 = f.read()
            image_data2 = base64.b64encode(image_data2)

        # using json data as python dictionary
        self.author = Author.objects.create(
                object_type = "author",
                uid = "lldbryq22g093jsm5sul7i339b6fljzkzxpd8tlf",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Frodo Baggins",
                profile_url = "http://127.0.0.1:5454/authors/lldbryq22g093jsm5sul7i339b6fljzkzxpd8tlf",
                author_github = "http://github.com/frodobaggins",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )

        # self.image = Post.objects.create_post(
        #
        #                                     )

        # valid author id (exists)
        post_data1 = {
                "type": "post",
                "title": "example post",
                "id": "764efa883dda1e11db476",
                "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
                "origin": "http://whereitcamefrom.com/posts/zzzzz",
                "description": "This post is an example",
                "contentType": "text/plain",
                "content": "testing... 1,2,3",
                "author": "lldbryq22g093jsm5sul7i339b6fljzkzxpd8tlf",
                "categories": ["web","tutorial"],
                "count": 5,
                "comments": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34/posts/764efa8e3dd81e11db4941/comments",
                "published": "2015-03-09T13:07:04+00:00",
                "visibility": "PUBLIC",
                "unlisted": False
                }

        # not valid author id (doesn't exist)
        post_data2 = {
                "type": "post",
                "title": "example post",
                "id": "764efa883bda1e11db576",
                "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
                "origin": "http://whereitcamefrom.com/posts/zzzzz",
                "description": "This post is an example",
                "contentType": "text/plain",
                "content": "testing... 1,2,3",
                "author": "9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "categories": ["web","tutorial"],
                "count": 5,
                "comments": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34/posts/764efa8e3dd81e11db4941/comments",
                "published": "2015-03-09T13:07:04+00:00",
                "visibility": "PUBLIC",
                "unlisted": False
                }

        # valid with image jpeg
        post_data3 = {
                "type": "post",
                "title": "example post",
                "id": "764esa883dna1e11db478",
                "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
                "origin": "http://whereitcamefrom.com/posts/zzzzz",
                "description": "This post is an example",
                "contentType": "text/plain, image/jpeg;base64",
                "content": "testing... 1,2,3",
                "image": image_data,
                "author": "lldbryq22g093jsm5sul7i339b6fljzkzxpd8tlf",
                "categories": ["web","tutorial"],
                "count": 5,
                "comments": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34/posts/764efa8e3dd81e11db4941/comments",
                "published": "2015-03-09T13:07:04+00:00",
                "visibility": "PUBLIC",
                "unlisted": False
                }

        self.post1 = Post.objects.create_post(post_data1)
        self.post2 = Post.objects.create_post(post_data2)
        self.post3 = Post.objects.create_post(post_data3)


    def test_post_model_is_valid(self):
        self.assertTrue(isinstance(self.post1, Post))
        self.assertFalse(isinstance(self.post2, Post))
        self.assertTrue(isinstance(self.post3, Post))

    def test_post_model_str(self):
        self.assertEqual(str(self.post1), "example post")
        self.assertNotEqual(str(self.post2), "example post")
        self.assertEqual(str(self.post3), "example post")


# class PlainTextPostTesting(TestCase):
#     def setUp(self):
#         # data for test_post_creation()
#         self.post_data = {
#                 "type": "post",
#                 "title": "Test Plain Text Post",
#                 "contentType": "text/plain",
#                 "content": "testing...123"
#                 }
#
#         self.post_data1 = {
#                 "type": "post",
#                 "contentType": "text/plain",
#                 "content": "testing...123"
#                 }
#
#         self.post_data2 = {
#                 "type": "post",
#                 "title": "Test Plain Text Post",
#                 "contentType": "text/plain",
#                 "content": "testing...123"
#                 }
#
#         self.post_data3 = {
#                 "type": "post",
#                 "title": "Test Plain Text Post",
#                 "contentType": "text/plain",
#                 "content": "testing...123"
#                 }
#
#     def test_post_creation(self):
#         url = reverse("index")
#         response = self.client.post(url, self.post_data)
#         self.assertEqual(response.status_code, 200)
#         pid = "http://127.0.0.1:5454/authors/2/posts/2"
#
#         try:
#             post = Post.objects.get(post_id = pid)
#         except Post.DoesNotExist:
#             post = None
#
#         self.assertIsNotNone(post)
#         self.assertEqual(post.object_type, "post")
#         self.assertEqual(post.title, "Test Plain Text Post")
#         self.assertEqual(post.content_type, "text/plain")
#         self.assertEqual(post.content, "testing...123")
#         self.assertEqual(post.post_source, "https://www.example.com/source")
#         self.assertEqual(post.post_origin, "https://www.example.com/origin")
#         self.assertEqual(post.comments, "http://127.0.0.1:5454/authors/2/posts/2/comments") # placeholder
#         self.assertEqual(post.comment_count, 0) # placeholder
#         self.assertEqual(post.is_unlisted, False)
#         self.assertEqual(post.visibility, "PUBLIC")
        # replace this later with a check on the actual datetime


    # def test_missing_title(self):
