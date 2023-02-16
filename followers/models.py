from django.db import models
from authors.models import Author
import uuid

MAX_LENGTH = 100
SMALLER_MAX_LENGTH = 50


# Create your models here.
'''
{
"type": "followers",
"items": [ {"type":"author",...}, ...]
}
'''
class Followers(Author):
    # many followers can be associated with an author
    follower_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='items', null=True, blank=True)

class FollowManager(models.Manager):

    def create_follow(self, author_following, author_followed):

        # create the summary statement by taking their first names
        author_following_first_name = author_following['displayName'].split(' ')[0]
        author_followed_first_name = author_followed['displayName'].split(' ')[0]
        summary = author_following_first_name + " wants to follow " + author_followed_first_name

        follow = self.create(follow_type = "Follow",
                            author_actor = author_following,
                            author_object = author_followed,
                            following_summary = summary
                            )
        return follow
    

class Follow(models.Model):
    follow_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    author_actor = models.JSONField() # dict containing information about the author
    author_object = models.JSONField()
    following_summary = models.CharField(max_length=SMALLER_MAX_LENGTH)
    objects = FollowManager()
