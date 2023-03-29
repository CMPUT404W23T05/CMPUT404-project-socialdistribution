from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author, Comment, Post
import uuid
from home.serializers import *
from home.remote_serializers import *
import requests

# creates an instance of author anytime a user is made (connects the 2 with one2one relation)

auth = {"https://socialdistcmput404.herokuapp.com/": {"Authorization": "Token d960c3dee9855f5f5df8207ce1cba7fc1876fedf"},
        "https://sd7-api.herokuapp.com/": {"Authorization": "Basic node01:P*ssw0rd!"},
        "https://social-t30.herokuapp.com/": {"Authorization": "Token 332af37c2a154de56cd8cb42644f1f81cc46c4ef"}}


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


@receiver(post_save, sender=Follow)
def create_remote_author(sender, instance, created, **kwargs):
    host = "https://social-t30.herokuapp.com/"
    if created:
        pass
        """
        if instance.author_actor["host"] != host:
            serializer = AuthorSerializer(data=instance.author_actor)
            if serializer.is_valid():
                Author.objects.create(**serializer.validated_data)
        """

@receiver(post_save, sender=Post)
def send_post_to_inbox(sender, instance, created, **kwargs):
 
    host = "https://social-t30.herokuapp.com/"

    # if a local post is created, send notification to local and remote authors (their followers)
    if created: 
        post = Post.objects.get(url_id=instance.url_id)

        followers_serializer = AuthorFollowersSerializer(post.author) # get the followers
        
        # for each follower
        for item in followers_serializer.data['items']:
            follower_host = item["host"] + "/" if not item["host"].endswith("/") else item["host"]

            if follower_host != host: # if it's a remote author
                post_serializer = PostForRemoteSerializer(post)
                follower_id = item["id"].split("/")[-1]
                url = follower_host + "api/authors/" + follower_id + "/inbox/" 

                headers = auth[follower_host] # get authorization
                r = requests.post(url, headers = headers, data=post_serializer.data) # post to inbox

            else: # it's a local author
                post_serializer = PostSerializer(post)
                get_follower = Author.objects.get(author_id = item['_id']) # get the author follower
                
                # notify each follower about the new post
                get_follower.inbox_items.create(inbox_item = post_serializer.data)


@receiver(post_save, sender=Comment)
def send_comment_to_inbox(sender, instance, created, **kwargs):


    # if a comment is created locally, send to inboxes
    # (now it depends on whether a comment was placed on a local or remote post)
    if created: 
        is_local_post = len(Post.objects.filter(url_id=instance.url_id)) # get the post based on its url
        comment = Comment.objects.get(url_id=instance.url_id) # get the comment based on its id

        if not is_local_post: # a local author commented on a remote post
            comment_serializer = CommentForRemoteSerializer(comment)
            comment_url = comment.url_id
            get_remote_author_info = comment_url.split('posts/')[0]
            host = comment_url.split('api/')[0]
            headers = auth[host] # get authorization
            url = get_remote_author_info + '/inbox/'
            r = requests.post(url, headers = headers, data=comment_serializer.data) # post to inbox

        else: # a local author commented on a local post
            
            comment_serializer = CommentSerializer(comment)
            post = is_local_post[0]
            author_serializer = AuthorSerializer(post.author)
            author_data = json.dumps(author_serializer.data)
            author_data_dict = json.loads(author_data)

            # get the author of the post (we need to send the comment notifcation to this author)
            author_of_post = Author.objects.get(author_id = author_data_dict['_id'])

            # the same author of the post might be the same author of the comment
            if author_data_dict['_id'] != str(comment.author.author_id): 
                author_of_post.inbox_items.create(inbox_item = comment_serializer.data)
