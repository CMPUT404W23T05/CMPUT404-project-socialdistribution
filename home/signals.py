
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author, Comment, Post
import uuid
from home.serializers import *
from home.remote_serializers import *
import requests

# creates an instance of author anytime a user is made (connects the 2 with one2one relation)

@receiver(post_save, sender=get_user_model())
def create_author(sender, instance, created, **kwargs):
    if created:
        uid = str(uuid.uuid4())
        Author.objects.create(
                # counts the number of comments on post any time a new instance of Comment is saved
                object_type = 'author',
                url_id = "https://social-t30.herokuapp.com/api/authors/" + uid,
                author_id = uid,
                home_host = "https://social-t30.herokuapp.com/",
                display_name = instance.username,
                profile_url = "https://social-t30.herokuapp.com/api/authors/" + uid,
                author_github = "",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg",
                user = instance
                )
        
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
    "https://sd-7-433-api.herokuapp.com/": {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')}}

    host = "https://social-t30.herokuapp.com/"

    # if a local post is created, send notification to local and remote authors (their followers)
    if created: 
        post = Post.objects.get(url_id=instance.url_id)

        # add post to their own inbox
        post_serializer = PostSerializer(post)
        post.author.inbox_items.create(inbox_item = post_serializer.data)
        followers_serializer = AuthorFollowersSerializer(post.author) # get the followers
  
        # for each follower
        for item in followers_serializer.data['items']:
            follower_host = item["host"] + "/" if not item["host"].endswith("/") else item["host"]
            if follower_host != host: # if it's a remote author

                if follower_host == "https://socialdistcmput404.herokuapp.com/":
                    post_serializer = PostForRemoteTenSerializer(post)
                else: # team 7
                    post_serializer = PostForRemoteSevenSerializer(post)

                follower_id = item["id"].split("/")[-1]
                url = follower_host + "api/authors/" + follower_id + "/inbox/" 
                headers = auth[follower_host] # get authorization

                data = json.loads(json.dumps(post_serializer.data))
                r = requests.post(url, headers = headers, json=data) # post to inbox
                if r.status_code == 500:
                    r = requests.post(url, headers = headers, json=data)

            else: # it's a local author
                post_serializer = PostSerializer(post)
                get_follower = Author.objects.get(url_id = item['id']) # get the author follower
                
                # notify each follower about the new post
                get_follower.inbox_items.create(inbox_item = post_serializer.data)


@receiver(post_save, sender=Comment)
def send_comment_to_inbox(sender, instance, created, **kwargs):

    auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
    "https://sd-7-433-api.herokuapp.com/": {"Authorization": "Basic "  + base64.b64encode(b'node01:P*ssw0rd!').decode('utf-8')}}

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