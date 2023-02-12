from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post

def index(request):
    return render(request, 'posts/index.html')

def make_post(request):
    if request.method == 'POST':
            # if request.content_type == 'application/json':
        # type = request.POST.get('type')
        # if type == 'post':
        #     message = "Post creation successful!"
        #     print(message)
        # else:
        #     message = "Post creation failed."
        #     print(message)
        #     title = request.POST.get('title')
        return redirect('')
    else:
        return(render(request), 'posts/index.html')

