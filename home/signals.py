from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author, Comment, Post
import uuid
from home.serializers import *
import requests
from django.core.cache import cache

# creates an instance of author anytime a user is made (connects the 2 with one2one relation)
@receiver(post_save, sender=get_user_model())
def create_author(sender, instance, created, **kwargs):
    if created:
        uid = str(uuid.uuid4())
        Author.objects.create(
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

# counts the number of comments on post any time a new instance of Comment is saved 
@receiver(post_save, sender=Comment)
def updated_post_count(sender, instance, created, **kwargs):
    if created:
        post = Post.objects.get(post_id=instance.post_id)
        post.comment_count = Comment.objects.filter(post_id=instance.post_id).count()
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

    # if a post is created, send notification to local and remote authors
    if created: 
        post = Post.objects.get(post_id=instance.post_id)
        post_serializer = PostSerializer(post)

        followers_serializer = AuthorFollowersSerializer(post.author) # get the followers
        
        # for each follower
        for item in followers_serializer.data['items']:
            follower_host = item["host"] # get the home host of follower

            if follower_host != host: # if it's a remote author
                follower_id = item["id"].split("/")[-1]
                if follower_host.endswith("/"): # home host may end with a "/"
                    url = follower_host + "api/authors/" + follower_id + "/inbox/" 
                else:
                    url = follower_host + "/api/authors/" + follower_id + "/inbox/" 

                headers = cache.get(follower_host) # get authorization
                r = requests.post(url, headers = headers, data=post_serializer.data) # post to inbox

            else: # it's a local author
                get_follower = Author.objects.get(author_id = item['_id']) # get the author follower
                
                # notify each follower about the new post
                get_follower.inbox_items.create(inbox_item = post_serializer.data)


@receiver(post_save, sender=Comment)
def send_comment_to_inbox(sender, instance, created, **kwargs):

    # if a comment is created locally
    # (if remotely, will be sent to our inbox by groups)
    if created: 
        post = Post.objects.get(post_id=instance.post_id) # get the post based on its id
        comment = Comment.objects.get(comment_id=instance.comment_id) # get the comment based on its id

        comment_serializer = CommentSerializer(comment)

        # find information about the author of the post
        author_serializer = AuthorSerializer(post.author)
        author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(author_data)

        # get the author of the post (we need to send the comment notifcation to this author)
        author_of_post = Author.objects.get(author_id = author_data_dict['_id'])

        # the same author of the post might be the same author of the comment
        if author_data_dict['_id'] != str(comment.author.author_id): 
            author_of_post.inbox_items.create(inbox_item = comment_serializer.data)


