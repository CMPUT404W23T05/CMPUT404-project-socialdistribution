from django.test import TestCase
from .models import Post
from datetime import datetime
from django.urls import reverse
from .models import Post

class ModelTesting(TestCase):

    def setUp(self):
        self.post = Post.objects.create(
                object_type = "post",
                title = "example post",
                post_id = "http://127.0.0.1:5454/authors/1/posts/1",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "this is an example post for testing",
                content_type = "text/plain",
                content = "testing... 1,2,3",
                comment_count = 0,
                comments = "http://127.0.0.1:5454/authors/1/posts/1/comments",
                pub_date = "2015-03-09T13:07:04+00:00",
                is_unlisted = False,
                visibility = "PUBLIC"
                )

    def test_post_model_is_valid(self):
        d = self.post
        self.assertTrue(isinstance(d, Post))

    def test_post_model_str(self):
        d = self.post
        self.assertEqual(str(d), "example post")


class PlainTextPostTesting(TestCase):
    
    def setUp(self):
        self.post_data = {
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
