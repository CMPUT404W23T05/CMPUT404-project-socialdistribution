from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Author)
admin.site.register(Authors)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Liked)
admin.site.register(Inbox)
admin.site.register(Followers)
admin.site.register(Follow)
admin.site.register(Comment)
