from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post
from datetime import datetime


'''
default view for posts page
'''
def index(request):
    if request.method == 'POST':
        object_type = request.POST.get('type')
        if object_type == 'post':
            if request.POST.get('contentType') == 'text/plain':
                plain_text_post(request)
            message = "Post creation successful!"
        else:
            message = "Post creation failed."
        return render(request, 'posts/index.html', {'message': message})
    else:
        return render(request, 'posts/index.html')

'''
make a public post
'''
def plain_text_post(request):
    post = Post()
    post.object_type = request.POST.get("type")
    post.title = request.POST.get("title")
    post.post_id = "http://127.0.0.1:5454/authors/2/posts/2" # need to actually generate a new id for post eventually

    # these are placeholdes for now, because I don't know how to deal with these yet
    post.post_source = "https://www.example.com/source"
    post.post_origin = "https://www.example.com/origin"
    post.description = "example description"
    post.comment_count = 0
    post.comments = "http://127.0.0.1:5454/authors/2/posts/2/comments"

    post.content_type = request.POST.get("contentType")
    post.content = request.POST.get("content")
    post.pub_date = datetime.utcnow().isoformat()  
    post.is_unlisted = False     # only true for image posts
    post.visibility = "PUBLIC"   # this is a public post, need to figure out how to pass whether its public or not
    post.save()


    
