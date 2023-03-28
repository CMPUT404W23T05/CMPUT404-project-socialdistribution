from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author, Comment, Post
import uuid
from home.serializers import *

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
                home_host = "https://social-t30.herokuapp.com",
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

    # if a post is created
    if created: 
        post = Post.objects.get(post_id=instance.post_id)
        post_serializer = PostSerializer(post)

        followers_serializer = AuthorFollowersSerializer(post.author) # get the followers
        
        # for each follower
        for item in followers_serializer.data['items']:
            get_follower = Author.objects.get(author_id = item['_id']) # get the author follower

            # notify each follower about the new post
            get_follower.inbox_items.create(inbox_item = post_serializer.data)


@receiver(post_save, sender=Comment)
def send_comment_to_inbox(sender, instance, created, **kwargs):

    # if a post is created
    if created: 
        post = Post.objects.get(post_id=instance.post_id) # get the post based on its id
        comment = Comment.objects.get(comment_id=instance.comment_id) # get the comment based on its id

        comment_serializer = CommentSerializer(comment)

        author_serializer = AuthorSerializer(post.author)
        author_data = json.dumps(author_serializer.data)
        author_data_dict = json.loads(author_data)

        # get the author of the post (we need to send the comment notifcation to this author)
        author_of_post = Author.objects.get(author_id = author_data_dict['_id'])

        # the same author of the post might be the same author of the comment
        if author_data_dict['_id'] != str(comment.author.author_id): 
            author_of_post.inbox_items.create(inbox_item = comment_serializer.data)
