
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author, Comment, Post
import uuid
from home.serializers import *
from home.remote_serializers import *
import requests
import sys

# creates an instance of author anytime a user is made (connects the 2 with one2one relation)

@receiver(post_save, sender=get_user_model())
def create_author(sender, instance, created, **kwargs):
    if created and (instance.username not in ['admin', 'anonymous']) and (not instance.username.startswith('team')):
        uid = str(uuid.uuid4())
        Author.objects.create(
                # counts the number of comments on post any time a new instance of Comment is saved
                object_type = 'author',
                url_id = "https://social-t30.herokuapp.com/authors/" + uid,
                author_id = uid,
                home_host = "https://social-t30.herokuapp.com/",
                display_name = instance.username,
                profile_url = "https://social-t30.herokuapp.com/authors/" + uid,
                author_github = "",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg",
                user = instance
                )

@receiver(post_save, sender=Remote)
def create_user_and_token_on_remote_create(sender, instance, created, **kwargs):
    if created:
        username = instance.name.lower()
        user = User.objects.create_user(username=username)

        token = Token.objects.create(user=user)

@receiver(post_delete, sender=Remote)
def delete_user_and_token_on_remote_delete(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.name.lower())
        user.delete()
    except User.DoesNotExist:
        pass

    try:
        token = Token.objects.get(user__username=instance.name.lower())
        token.delete()
    except Token.DoesNotExist:
        pass


        
@receiver(post_save, sender=Comment)
def updated_post_count(sender, instance, created, **kwargs):
    if created:
        post = Post.objects.get(post_id=instance.post_id)
        post.comment_count = Comment.objects.filter(
            post_id=instance.post_id).count()
        post.save()

@receiver(post_save, sender=Post)
def send_post_to_inbox(sender, instance, created, **kwargs):

    auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
    "https://sd-7-433-api.herokuapp.com/": {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')},
    "https://ultimate-teapot.herokuapp.com/": "Basic "  + base64.b64encode(b'team5:jN2!42GUtCgB').decode('utf-8')}

    host = "https://social-t30.herokuapp.com/"

    # if a local post is created, send notification to local and remote authors (their followers)
    if created and instance.visibility in ["PUBLIC", "FRIENDS"]: 
        post = Post.objects.get(url_id=instance.url_id)

        # add post to their own inbox
        post_serializer = PostSerializer(post)
        post_data_dict = json.loads(json.dumps(post_serializer.data))

        post.author.inbox_items.create(inbox_item = post_data_dict)
        followers_serializer = AuthorFollowersSerializer(post.author) # get the followers
  
        # for each follower
        for item in followers_serializer.data['items']:
            follower_host = item["host"] + "/" if not item["host"].endswith("/") else item["host"]
            if follower_host != host: # if it's a remote author
                
                # different groups may format their post differently
                if follower_host == "https://socialdistcmput404.herokuapp.com/":
                    post_serializer = PostForRemoteTenSerializer(post)
                elif follower_host == "https://sd-7-433-api.herokuapp.com/":
                    post_serializer = PostForRemoteSevenSerializer(post)
                else: # sending to team 9 (e.g. https://ultimate-teapot.herokuapp.com/main/api/authors/d487324f-e41a-402c-a726-6916161695bf/inbox/)
                    post_serializer = PostSerializer(post)
                    follower_host = follower_host + "main/"

                follower_id = item["id"].split("/")[-1]
                url = follower_host + "api/authors/" + follower_id + "/inbox/" 
                headers = auth[follower_host] # get authorization

                data = json.loads(json.dumps(post_serializer.data))
                data["categories"] = ["post"] if "categories" not in data.keys() else False

                r = requests.post(url, headers = headers, json=data) # post to inbox
                if r.status_code == 500:
                    r = requests.post(url, headers = headers, json=data)
                print(r.status_code)
                sys.stdout.flush()
            else: # it's a local author
                post_serializer = PostSerializer(post)
                data = json.loads(json.dumps(post_serializer.data))
                data["categories"] = ["post"] if "categories" not in data.keys() else False

                get_follower = Author.objects.get(url_id = item['id']) # get the author follower
                
                # notify each follower about the new post
                get_follower.inbox_items.create(inbox_item = data)


@receiver(post_save, sender=Comment)
def send_comment_to_inbox(sender, instance, created, **kwargs):

    auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
    "https://sd-7-433-api.herokuapp.com/": {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')},
    "https://ultimate-teapot.herokuapp.com/": "Basic "  + base64.b64encode(b'team5:jN2!42GUtCgB').decode('utf-8')}

    host = "https://social-t30.herokuapp.com/"

    # if a comment is created locally, send to inbox of the author who made the post
    if created and instance.author.home_host == host: 

        local_post = Post.objects.filter(post_id=instance.post_id) # get the post based on its url
        comment = Comment.objects.get(url_id=instance.url_id) # get the comment based on its id

        comment_serializer = CommentSerializer(comment)
        post = local_post[0]

        author_serializer = AuthorSerializer(post.author)
        author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(author_data)

        # get the author of the post (we need to send the comment notifcation to this author)
        author_of_post = Author.objects.get(url_id = author_data_dict['url'])

        # the same author of the post might be the same author of the comment
        if author_data_dict['url'] != str(comment.author.url_id): 
            author_of_post.inbox_items.create(inbox_item = comment_serializer.data)
