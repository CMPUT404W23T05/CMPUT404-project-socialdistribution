from django.db import models

MAX_LENGTH = 100
SMALLER_MAX_LENGTH = 50

class Author(models.Model):
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    # unique=True here is allowing uid to be used as a secondary key/ foreign key
    uid = models.URLField(max_length=MAX_LENGTH, unique=True)  # ID of the author
    home_host = models.URLField() # the home host
    display_name = models.CharField(max_length=MAX_LENGTH) # the display name
    profile_url = models.URLField(max_length=MAX_LENGTH) # url to the author's profile
    author_github = models.URLField(max_length=MAX_LENGTH) # HATEOS url for Github API
    profile_image = models.URLField(max_length=MAX_LENGTH) # Image from a public domain (or ImageField?)

    def __str__(self):
        # clearer description of object itself rather than Author(1) in admin interface
        return self.display_name

class Authors(models.Model):
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)


class Post(models.Model):
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    title =  models.CharField(max_length=MAX_LENGTH) # title of a post
    post_id = models.URLField(max_length=MAX_LENGTH, unique=True) # id of a post
    post_source = models.URLField(max_length=MAX_LENGTH) # where did you get this post from?
    post_origin =  models.URLField(max_length=MAX_LENGTH) # where is it actually from
    description = models.TextField(max_length=MAX_LENGTH) # a brief description of the post
    content_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    content = models.TextField(max_length=MAX_LENGTH)
    # author = models.ForeignKey(Author, on_delete=models.CASCADE) # an author can write many posts
    # put in categories here (id = models.AutoField(primary_key=True, null=True)i.e. tags): a list of string
    comment_count = models.IntegerField()
    comments = models.URLField(max_length=MAX_LENGTH)
    # commentsSrc is OPTIONAL and can be missing
    pub_date = models.DateTimeField()
    is_unlisted = models.BooleanField()
    visibility = models.CharField(max_length=SMALLER_MAX_LENGTH, default="FRIENDS")

    def __str__(self):
        return self.title

class ImagePost(models.Model):
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

class Like(models.Model):
    """
    LikeManager() takes care of creating the objects for us.

    Example:
    - Like.objects.create_like(context_url, author_liking, object_url)
    """
    context = models.URLField(max_length=MAX_LENGTH)
    like_summary = models.CharField(max_length=SMALLER_MAX_LENGTH)
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    author_object = models.JSONField(null=True) # the author that liked your post
    obj = models.URLField(max_length=MAX_LENGTH) # the post/comment that got liked

    associated_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name = 'liked_items', null=True, blank=True)

    objects = LikeManager() # creates the object and adds a summary along with it

class Liked(models.Model): # may not need to be used?
    context = models.URLField(max_length=MAX_LENGTH)

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
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    author_actor = models.JSONField(null=True) # dict containing information about the author
    author_object = models.JSONField(null=True)
    following_summary = models.CharField(max_length=SMALLER_MAX_LENGTH, null=True)
    objects = FollowManager()

class Comments(models.Model):
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    page =  models.IntegerField()
    size = models.IntegerField()
    post = models.URLField(max_length=MAX_LENGTH)
    comments_id = models.URLField(max_length=MAX_LENGTH)

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
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    author_json = models.JSONField(null=True, blank=True)
    comment_content = models.TextField(max_length=MAX_LENGTH)
    content_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    pub_date = models.DateTimeField()
    comment_id = models.URLField(max_length=MAX_LENGTH, unique=True)

    comments = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name = 'comments_list', null=True, blank=True)
    associated_author =  models.ForeignKey(Author, on_delete=models.CASCADE, related_name = 'comment_items', null=True, blank=True)