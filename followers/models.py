from django.db import models
from authors.models import Author

MAX_LENGTH = 100
SMALLER_MAX_LENGTH = 50


# Create your models here.
'''
{
"type": "followers",
"items": [ {"type":"author",...}, ...]
}
'''
<<<<<<< HEAD
class Followers(Author):
    # follower is an author
    follower_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    follower_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers_info')
   
=======
class Followers(models.Model):
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)


>>>>>>> 695d04881396655648c793af1eab83c6d5c1dc14

class Follow(models.Model):
    object_type = models.CharField(max_length=SMALLER_MAX_LENGTH)
    # put in summary here
   # actor = models.ForeignKey(Author, on_delete=models.CASCADE)
   # object = models.ForeignKey(Author, on_delete=models.CASCADE)
