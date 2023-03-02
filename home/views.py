from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from .models import Post
from datetime import datetime

# parsing data from the client
from rest_framework.parsers import JSONParser
# To bypass having a CSRF token
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


from .serializers import *
from .models import *

'''
view for login
'''
def login(request):
    pass


'''
default view for home page
'''
def index(request):
    # this below is just the code to handle creating a post
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
make a public plain text post
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


@csrf_exempt
def followers(request, author_id):
    '''
    List all followers of an author 
    (AUTHOR_ID being integer ids 1,2,3... for the time being)

    Handles URL: ://service/authors/{AUTHOR_ID}/follower
    '''
    try:
        selected_author = Author.objects.filter(id=author_id)[0]
        serializer = AuthorFollowersSerializer(selected_author)
    except IndexError: # that id does not exist
        return HttpResponse(status=404)  
    
    if (request.method == 'GET'):
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def followers_details(request, author_id, follower_id):
    '''
    Handles the details related to:
    URL: ://service/authors/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}

    (AUTHOR_ID being integer ids 1,2,3... for the time being)
    '''
    try:
        selected_author = Author.objects.filter(id=author_id)[0]
    except IndexError: # that id does not exist
        return HttpResponse(status=404)  
    
    if (request.method == 'DELETE'):
        selected_follower = selected_author.followers_items.filter(id=follower_id)[0]
        selected_follower.delete()
        return HttpResponse(status=200)  

    elif(request.method == 'PUT'):
        selected_follower = Author.objects.filter(id=follower_id)[0]
        selected_author.followers_items.create(**model_to_dict(selected_follower))
        return HttpResponse(status=200)  

    elif(request.method == 'GET'):
        try:
            selected_follower= Author.objects.filter(id=follower_id)[0]
        except IndexError: # that id does not exist
            return HttpResponse(status=404)  
        else:
           return HttpResponse(status=200)  
        
@csrf_exempt
def following_details(request, author_id):
    try:
        # selected_author = Author.objects.values('display_name', 'profile_image', 'followers_items')
        selected_author = Author.objects.filter(followers_items__id= author_id).values('display_name', 'profile_image', 'followers_items')
        if not len(selected_author):
            raise IndexError

    except IndexError: # that id does not exist
        return HttpResponse(status=404)
      
    if(request.method == 'GET'):
        pass

@csrf_exempt
def friends_details(request, author_id):
    try:
        # who is the author currently following?
        author_followings = Author.objects.filter(followers_items__id= author_id)
        selected_author = Author.objects.filter(id= author_id)[0].followers_items.all() 
    
    except IndexError: # that id does not exist
        return HttpResponse(status=404)
      
    if(request.method == 'GET'):
        pass

@csrf_exempt
def requests_details(request, author_id):
    try:
        # who is the author currently following?
        follows = Follow.objects.all()
    except:
        pass