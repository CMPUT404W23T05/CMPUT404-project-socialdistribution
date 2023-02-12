from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post


# def index(request):
#     return render(request, 'posts/index.html')

def index(request):
    if request.method == 'POST':
            # if request.content_type == 'application/json':
        object_type = request.POST.get('type')
        if object_type == 'post':
            message = "Post creation successful!"
        else:
            message = "Post creation failed."
            title = request.POST.get('title')
        return render(request, 'posts/index.html', {'message': message})
    else:
        return render(request, 'posts/index.html')

