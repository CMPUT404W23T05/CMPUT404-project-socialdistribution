from django.urls import path, include

from home import views

app_name = 'home'
urlpatterns = [
        path('', views.login, name='login'),
        path('home/', views.index, name='index'),
        path('posts/', views.GetPosts.as_view()),
        path('create-post/', views.CreatePost.as_view()),
]
