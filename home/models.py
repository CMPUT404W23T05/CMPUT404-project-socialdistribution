# from django.contrib.postgres.fields import ArrayField
from django.db import models, IntegrityError
from django.core.files.base import ContentFile
from django.core.files import File
from io import BytesIO
from PIL import Image
import base64
from django.contrib.auth.models import User

import json

CONTENT_MAX_LENGTH = 10000  # for content field
URL_MAX_LENGTH = 2000       # for urls
COMMENT_MAX_LENGTH = 200    # for comment length
ID_MAX_LENGTH = 50          # for ids
BIG_MAX_LENGTH = 80         # for longer fields like 'title'
SMALL_MAX_LENGTH = 30       # for short fields like 'type'




###################### Models Managers #########################################
class LikeManager(models.Manager):

    # to create a like, call create_like and pass in these arguments
    def create_like(self, context_url, author_liking, object_url):
        """
        Input:
        - context_url: the @context link as a string
        - author_liking: Author JSON object as a dict
        - object_url: the link of what was liked (could be a post or comment) as a string
        """
        # create the summary statement by taking the first name of the author giving a like
        author_liking_name = author_liking["displayName"]
        author = Author.objects.filter(profile_url = author_liking["url"])


        # an author can like posts and comments
        if "comments" in object_url:
            summary = author_liking_name + " Likes your comment"
        else:
            summary = author_liking_name + " Likes your post"

        if len(author) > 0: # we're working with a local author who gave a like
            like = self.create(
                            context = context_url,
                            like_summary = summary,
                            object_type = "Like",
                            author_object = author_liking,
                            obj = object_url,
                            associated_author = author[0]
                            )
            
        else: # we're working with a remote author who gave a like
            like = self.create(
                            context = context_url,
                            like_summary = summary,
                            object_type = "Like",
                            author_object = author_liking,
                            obj = object_url,
                            )

        like.save()
        return like
    
    def delete_like(self):
        self.delete()
    

class FollowManager(models.Manager):

    def create_follow(self, author_following, author_followed, state=None):
        """
        Input:
        - author_following: Author object as a dict
        - author_followed: Author object as a dict
        """
        # create the summary statement by taking their first names
       
        author_following_first_name = author_following['displayName'].split(' ')[0]
        author_followed_first_name = author_followed['displayName'].split(' ')[0]
        summary = author_following_first_name + " wants to follow " + author_followed_first_name

        follow = self.create(object_type = "Follow",
                            author_actor = author_following,
                            author_object = author_followed,
                            state = "Pending" if not state else state,
                            following_summary = summary
                            )
        follow.save()
        return follow

    def delete_follow(self):
        self.delete()

####################### Models #################################################
class Remote(models.Model):
    name = models.CharField(max_length=SMALL_MAX_LENGTH, default='TEAM')
    url = models.URLField(max_length=URL_MAX_LENGTH, unique=True, null=False, blank=False)
    token = models.CharField(max_length=BIG_MAX_LENGTH, null=True, blank=True)
    basic = models.CharField(max_length=BIG_MAX_LENGTH, null=True, blank=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    url_id = models.URLField(max_length=URL_MAX_LENGTH, unique=True, null=False, blank=False)
    author_id = models.UUIDField(max_length=BIG_MAX_LENGTH, unique=True, null=True, blank=True)  # ID of the author
    home_host = models.URLField(max_length=URL_MAX_LENGTH) # the home host
    display_name = models.CharField(max_length=SMALL_MAX_LENGTH) # the display name
    profile_url = models.URLField(max_length=URL_MAX_LENGTH) # url to the author's profile
    author_github = models.URLField(max_length=URL_MAX_LENGTH, blank=True, null=True) # HATEOS url for Github API
    profile_image = models.URLField(max_length=URL_MAX_LENGTH) # Image from a public domain (or ImageField?)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author', null=True, blank=False) # this is for user/author creation

    def __str__(self):
        # clearer description of object itself rather than Author(1) in admin interface
        return self.display_name


class Post(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH, null=False)
    title =  models.CharField(max_length=BIG_MAX_LENGTH, null=True) # title of a post
    url_id = models.URLField(max_length=URL_MAX_LENGTH, unique=True, null=False, blank=False)
    post_id = models.UUIDField(max_length=ID_MAX_LENGTH, unique=True, null=True, blank=True) # id of a post
    post_source = models.URLField(max_length=URL_MAX_LENGTH, null=True) # where did you get this post from?
    post_origin =  models.URLField(max_length=URL_MAX_LENGTH, null=True) # where is it actually from
    description = models.TextField(max_length=BIG_MAX_LENGTH, null=True, blank=True) # a brief description of the post
    content_type = models.CharField(max_length=BIG_MAX_LENGTH, null=True)
    content = models.TextField(max_length=CONTENT_MAX_LENGTH, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, to_field='author_id', related_name='posts', null=False)
    categories = ArrayField(models.CharField(max_length=BIG_MAX_LENGTH), blank=True, null=True)
    comment_count = models.IntegerField(null=True)
    comments = models.URLField(max_length=URL_MAX_LENGTH, null=True)
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_unlisted = models.BooleanField(null=False)
    visibility = models.CharField(max_length=SMALL_MAX_LENGTH, default="PUBLIC", null=False)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title

    def get_image(self):
        if not self.image:
            return None
        
        image_data = base64.b64decode(self.image)

        if 'image/png' in self.content_type:
            content_type = "image/png"
        elif 'image/jpeg' in self.content_type:
            content_type = "image/jpeg"
        elif 'image/jpg' in self.content_type:
            content_type = "image/jpeg"
        else:
            content_type = None

        return image_data, content_type


class Like(models.Model):
    """
    LikeManager() takes care of creating the objects for us.

    Example:
    - Like.objects.create_like(context_url, author_liking, object_url)
    """
    context = models.URLField(max_length=URL_MAX_LENGTH)
    like_summary = models.CharField(max_length=BIG_MAX_LENGTH)
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    author_object = models.JSONField(null=True) # the author that liked your post
    obj = models.URLField(max_length=URL_MAX_LENGTH) # the post/comment that got liked

    associated_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name = 'liked_items', null=True, blank=True)

    objects = LikeManager() # creates the object and adds a summary along with it
    
    def __str__(self):
        return self.author_object["displayName"] + " liked something"

class Inbox(models.Model):
    """
    An author will have many items in their inbox.

    Example of adding a "notification" to their inbox:
    - a = Author.objects.create(..display_name=...profile_url=...)
    - a.inbox_items.create(...add a JSON dict as such as for a Follow request ...)
    """
    inbox_item = models.JSONField(null=True, blank=True)
    associated_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='inbox_items', null=True, blank=True)

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return self.associated_author.display_name + ": " + self.inbox_item["type"]
    
class Follower(models.Model):
    """
    Example of adding a follower:
    - a = Author.objects.create(..display_name=...profile_url=...)

    - a.followers_items.create(author_info = {display_name: ..., profile_url: ...})
    """
    author_info = models.JSONField(null=True, blank=True)
    follower_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers_items', null=True, blank=True)
    
    def __str__(self):
        return self.author_info["displayName"] + "  is following  " + self.follower_author.display_name

class Follow(models.Model):
    """
    FollowManager() takes care of creating the objects for us.

    Example:
    - Follow.objects.create_follow(author_following, author_followed)
    """
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    author_actor = models.JSONField() # dict containing information about the author
    author_object = models.JSONField()
    following_summary = models.CharField(max_length=BIG_MAX_LENGTH)
    state = models.CharField(max_length=SMALL_MAX_LENGTH)
    objects = FollowManager()

    def __str__(self):
        return self.following_summary
    


class Comment(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    url_id = models.URLField(max_length=URL_MAX_LENGTH, unique=True, null=False, blank=False)
    comment_id = models.UUIDField(max_length=ID_MAX_LENGTH, unique=True, null=False, blank=False)
    post_id = models.UUIDField(max_length=ID_MAX_LENGTH, null=False, blank=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, to_field='author_id', related_name='comments', null=False)
    content = models.TextField(max_length=COMMENT_MAX_LENGTH, blank=True, null=True)
    content_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ('-pub_date',)
