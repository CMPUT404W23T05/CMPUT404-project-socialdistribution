from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Author
import uuid

@receiver(post_save, sender=get_user_model())
def create_author(sender, instance, created, **kwargs):
    if created:
        uid = str(uuid.uuid4())
        Author.objects.create(
                object_type = 'author',
                uid = uid,
                home_host = "http://127.0.0.1:8000/",
                display_name = instance.username,
                profile_url = "http://127.0.0.1:8000/authors/" + uid,
                author_github = "",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg",
                user = instance
                )
