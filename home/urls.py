from django.urls import path, include

from home import views
from .views import index, login, GetLatestPosts

app_name = 'home'
urlpatterns = [
        path('', views.login, name='login'),
        path('home/', views.index, name='index'),
        path('posts/', views.GetLatestPosts.as_view()),
]
