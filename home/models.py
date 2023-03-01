from django.db import models, IntegrityError
# from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.core.files import File
from io import BytesIO
from PIL import Image
import base64

CONTENT_MAX_LENGTH = 10000  # for content field
URL_MAX_LENGTH = 2000       # for urls
COMMENT_MAX_LENGTH = 200    # for comment length
ID_MAX_LENGTH = 50          # for ids
BIG_MAX_LENGTH = 80         # for longer fields like 'title'
SMALL_MAX_LENGTH = 20       # for short fields like 'type'




###################### Models Managers #########################################
class PostManager(models.Manager):
#     def create_post(self, request_body):
#         """
#         takes request body and checks what kind of post is being created, and
#         then calls the correct function
#         Input:
#         - request_body: the body of POST request as python dictionary
#         Output:
#         - returns either Post instance or error message
#         """
#
#         if request_body['contentType'] == 'application/base64':
#             return self.create_post_from_base64(request_body)
#         else:
#             return self.create_text_post(request_body)
#
#     def create_text_post(self, request_body):
#         """
#         creates a plain text post and stores it in the data base
#         Input:
#         - request_body: the body of POST request as python dictionary
#         Output:
#         - returns either Post instance or error message
#         """
#         if not('image' in request_body and 'content' in request_body):
#             pass #put something here to say you can't make post with image or content
#
#         contentType = request_body['contentType']
#         if 'content' in request_body:
#             content_data = request_body['content']
#         else:
#             content_data = None
#
#         if ('image' in request_body and
#             ('image/jpeg;base64' in contentType or 'image/png;base64' in contentType)):
#             image_data = base64.b64decode(request_body['image'])
#             image_file = ContentFile(image_data, name='test_image')
#             image_obj = Image.objects.create(image=image_file)
#         else:
#             image_obj = None
#
#         try:
#             post = self.create(
#                                 object_type = request_body['type'],
#                                 title = request_body['title'],
#                                 post_id = request_body['id'],
#                                 post_source = request_body['source'],
#                                 post_origin = request_body['origin'],
#                                 description = request_body['description'],
#                                 content_type = request_body['contentType'],
#                                 content = request_body['content'],
#                                 image = image_obj,
#                                 author = Author.objects.get(uid=request_body['author']),
#                                 # categories = request_body['categories'],
#                                 comment_count = request_body['count'],
#                                 comments = request_body['comments'],
#                                 # commentSrc = request_body[''],
#                                 pub_date = request_body['published'],
#                                 is_unlisted = request_body['unlisted'],
#                                 visibility = request_body['visibility']
#                                 )
#             # post.image.parent_post = post
#             return post
#
#         except IntegrityError:
#             return "violation of database integrity constraints"
#         except Author.DoesNotExist:
#             return "Author object does not exist"
#
#     def create_post_from_base64(self, request_body):
#         pass
    pass



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
        author_liking_name = author_liking['displayName']

        # an author can like posts and comments
        if "comments" in object_url:
            summary = author_liking_name + " Likes your comment"
        else:
            summary = author_liking_name + " Likes your post"

        like = self.create(
                            context = context_url,
                            like_summary = summary,
                            object_type = "Like",
                            author_object = author_liking,
                            obj = object_url
                            )
        return like



####################### Models #################################################
class Author(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    # unique=True here is allowing uid to be used as a secondary key/ foreign key
    uid = models.UUIDField(max_length=BIG_MAX_LENGTH, unique=True, null=False, blank=False)  # ID of the author
    home_host = models.URLField(max_length=URL_MAX_LENGTH) # the home host
    display_name = models.CharField(max_length=SMALL_MAX_LENGTH) # the display name
    profile_url = models.URLField(max_length=URL_MAX_LENGTH) # url to the author's profile
    author_github = models.URLField(max_length=URL_MAX_LENGTH) # HATEOS url for Github API
    profile_image = models.URLField(max_length=URL_MAX_LENGTH) # Image from a public domain (or ImageField?)

    def __str__(self):
        # clearer description of object itself rather than Author(1) in admin interface
        return self.display_name


class Authors(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)


# class Image(models.Model):
#     image = models.ImageField(upload_to ='images/')


class Post(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH, null=False)
    title =  models.CharField(max_length=BIG_MAX_LENGTH, null=True) # title of a post
    post_id = models.UUIDField(max_length=ID_MAX_LENGTH, unique=True, null=False, blank=False) # id of a post
    post_source = models.URLField(max_length=URL_MAX_LENGTH, null=False) # where did you get this post from?
    post_origin =  models.URLField(max_length=URL_MAX_LENGTH, null=False) # where is it actually from
    description = models.TextField(max_length=BIG_MAX_LENGTH, null=True) # a brief description of the post
    content_type = models.CharField(max_length=SMALL_MAX_LENGTH, null=False)
    content = models.TextField(max_length=CONTENT_MAX_LENGTH, null=True, blank=True)
    # image = models.OneToOneField(Image, on_delete=models.CASCADE, related_name='post', null=True)
    image = models.ImageField(upload_to ='images/', blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, to_field='uid',
                               related_name='posts', null=False)
    # put in categories here i.e. tags): a list of string
    # categories = ArrayField(models.CharField(max_length=SMALLER_MAX_LENGTH), blank=True, null=True)
    comment_count = models.IntegerField(null=True)
    comments = models.URLField(max_length=URL_MAX_LENGTH, null=True)
    # commentsSrc is OPTIONAL and can be missing
    pub_date = models.DateTimeField(auto_now_add=True, null=False)
    is_unlisted = models.BooleanField(null=False)
    visibility = models.CharField(max_length=SMALL_MAX_LENGTH, default="FRIENDS", null=False)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''


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


class Liked(models.Model): # may not need to be used?
    context = models.URLField(max_length=URL_MAX_LENGTH)


class Inbox(models.Model):
    """
    An author will have many items in their inbox.

    Example of adding a "notification" to their inbox:
    - a = Author.objects.create(..display_name=...profile_url=...)
    - a.inbox_items.create(...add a JSON dict as such as for a Follow request ...)
    """
    inbox_item = models.JSONField(null=True, blank=True)
    associated_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='inbox_items', null=True, blank=True)


class Followers(Author):
    """
    A follower is an author.

    Example of adding a follower:
    - a = Author.objects.create(..display_name=...profile_url=...)
    - a.followers_items.create(..display_name=...profile_url=...)
    """
    follower_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers_items', null=True, blank=True)


class FollowManager(models.Manager):

    def create_follow(self, author_following, author_followed):
        """
        Input:
        - author_following: Author JSON object as a dict
        - author_followed: Author JSON object as a dict
        """
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
    """
    FollowManager() takes care of creating the objects for us.

    Example:
    - Follow.objects.create_follow(author_following, author_followed)
    """
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    author_actor = models.JSONField(null=True) # dict containing information about the author
    author_object = models.JSONField(null=True)
    following_summary = models.CharField(max_length=BIG_MAX_LENGTH, null=True)
    objects = FollowManager()


class Comments(models.Model):
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    page =  models.IntegerField()
    size = models.IntegerField()
    post = models.URLField(max_length=URL_MAX_LENGTH)
    comments_id = models.URLField(max_length=URL_MAX_LENGTH)


class Comment(models.Model):
    """
    The last two variables describe the relationships.
    1. Comments can contain many Comment
        - Example of adding a comment:
        - c = Comments.objects.create(...page=...size=...)
        - c.comments_list.create(...comment_content=...content_type=...)

    2. An author can be associated with many Comment
        - Example of adding a comment:
        - a = Author.objects.create(...)
        - a.comment_items.create(...comment_content=...content_type=...)
    """
    object_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    author_json = models.JSONField(null=True, blank=True)
    comment_content = models.TextField(max_length=COMMENT_MAX_LENGTH)
    content_type = models.CharField(max_length=SMALL_MAX_LENGTH)
    pub_date = models.DateTimeField()
    comment_id = models.URLField(max_length=ID_MAX_LENGTH, unique=True)

    comments = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name = 'comments_list', null=True, blank=True)
    associated_author =  models.ForeignKey(Author, on_delete=models.CASCADE, related_name = 'comment_items', null=True, blank=True)
