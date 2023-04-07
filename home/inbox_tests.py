
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
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

class InboxTesting(TestCase):
    def setUp(self):

        self.factory = APIRequestFactory()
 
        self.user = User.objects.create_user(
        username='user', password='pass')

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
                "url_id": "https://social-t30.herokuapp.com/api/authors/38f57b34-f1ff-4f3b-9e81-2be731a14a0e",
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
        '''
        self.comment_for_author_1 = Comment.objects.create(
                object_type = "comment",
                url_id = "https://social-t30.herokuapp.com/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b/comments/73fe120d-1f19-44e4-9a7f-c184b7df5597",
                comment_id = "73fe120d-1f19-44e4-9a7f-c184b7df5597",
                post_id =  "d091e3f1-4482-4d9d-8673-ac913f44fb9b",
                author = self.author2,
                content = "I am author 2!",
                content_type = "text/plain"
                )
        '''

    def test_follows(self):

        # add author 1 (our "remote" author) as a follower of author 2
        serializer = AuthorSerializer(self.author)
        author_data = json.dumps(serializer.data)
        author_data_dict = json.loads(author_data)

        serializer2 = AuthorSerializer(self.author2)
        author_data2= json.dumps(serializer2.data)
        author_data_dict2 = json.loads(author_data2)

        # author 1 sent a follow request to author 2
        follow = Follow.objects.create_follow(author_data_dict, author_data_dict2)
        follow_serializer = FollowSerializer(follow)

        self.author2.followers_items.create(author_info = author_data_dict)
        self.assertEqual(len(self.author2.followers_items.all()), 1)

    def test_receiving_comment_from_remote_author(self):

        example_comment = {
        "id": "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b/comments/760f6803-e249-456f-b5e5-e0d6478bb182",
        "type": "comment",
        "author":  {
            "type": "author",
            "id": "https://socialdistcmput404.herokuapp.com/authors/3aebd5d7-4853-437c-8af0-b46ab4c40dfa",
            "host": "https://socialdistcmput404.herokuapp.com/",
            "displayName": "team5",
            "github": "",
            "profileImage": "",
            "type": "author",
            "url": "https://socialdistcmput404.herokuapp.com/authors/3aebd5d7-4853-437c-8af0-b46ab4c40dfa"
            },
        "comment": "test",
        "contentType": "text/plain"
        }
        
        # also works without the _id for the author
        comment_json_dict = json.dumps(example_comment)
        request = self.factory.post('/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/inbox/', comment_json_dict, content_type='application/json')
        force_authenticate(request, user=self.user)

        response = InboxDetails.as_view()(request, author_id = "d569cd39-0a2d-411e-8d86-e8a063a18dea")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.author.inbox_items.filter(inbox_item__type = "comment"))
        
        post = Post.objects.get(url_id = example_comment["id"].split('/comments/')[0])
        self.assertEqual(post.comment_count, 1)

    def test_receiving_like_from_remote_author(self):
        example_like = {
            "type": "Like",
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": "testuser1 Likes your post",
            "object": "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b",
            "author": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea",
                "host": "http://127.0.0.1:8000/",
                "displayName": "testuser1",
                "url": "http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea",
                "github": "",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                
            }
        }
        # also works without the _id for the author
        comment_json_dict = json.dumps(example_like)
        request = self.factory.post('/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/inbox/', comment_json_dict, content_type="application/json")
        force_authenticate(request, user=self.user)
        
        response = InboxDetails.as_view()(request, author_id = "d569cd39-0a2d-411e-8d86-e8a063a18dea")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.author.inbox_items.filter(inbox_item__type = "Like"))

        request = self.factory.get("http://127.0.0.1:8000/api/authors/d569cd39-0a2d-411e-8d86-e8a063a18dea/posts/d091e3f1-4482-4d9d-8673-ac913f44fb9b/likes")
        force_authenticate(request, user=self.user)
        response = PostLikes.as_view()(request, author_id = "d569cd39-0a2d-411e-8d86-e8a063a18dea", post_id = "d091e3f1-4482-4d9d-8673-ac913f44fb9b")

        self.assertEqual(response.status_code, 200)
 