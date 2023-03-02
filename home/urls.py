from django.urls import path
from . import views

urlpatterns = [
        path('', views.login, name='login'),
        path('home/', views.index, name='index'),
        path('followers/', views.followers, name='followers'),
        path('followers/<int:follower_id>/', views.followers_details, name="followers_details"),
        path('following/', views.following_details, name="following_details"),
        path('friends/', views.friends_details, name="friends_details"),
        path('requests/', views.requests_details, name="requests_details"),
]
