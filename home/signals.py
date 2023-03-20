from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author, Comment, Post
import uuid

# creates an instance of author anytime a user is made (connects the 2 with one2one relation)
@receiver(post_save, sender=get_user_model())
def create_author(sender, instance, created, **kwargs):
    if created:
        uid = str(uuid.uuid4())
        Author.objects.create(
                object_type = 'author',
                url_id = "http://127.0.0.1:8000/authors/" + uid,
                author_id = uid,
                home_host = "http://127.0.0.1:8000/",
                display_name = instance.username,
                profile_url = "http://127.0.0.1:8000/authors/" + uid,
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
