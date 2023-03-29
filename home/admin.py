from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Remote)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Inbox)
admin.site.register(Follower)
admin.site.register(Follow)
admin.site.register(Comment)
