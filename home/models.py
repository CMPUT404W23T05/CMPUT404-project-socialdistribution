from django.db import models

MAX_LENGTH = 100
SMALLER_MAX_LENGTH = 50

class Post(models.Model):
    # "type": "post"
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    title =  models.CharField(max_length=MAX_LENGTH) # title of a post
    post_id = models.URLField(max_length=MAX_LENGTH) # id of a post
    post_source = models.URLField(max_length=MAX_LENGTH) # where did you get this post from?
    post_origin =  models.URLField(max_length=MAX_LENGTH) # where is it actually from
    description = models.TextField(max_length=MAX_LENGTH) # a brief description of the post
    content_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    content = models.TextField(max_length=MAX_LENGTH)
    # author = models.ForeignKey(Author, on_delete=models.CASCADE) # an author can write many posts
    # put in categories here: a list of string
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
