from django.urls import path, include

from home import views

app_name = 'home'
urlpatterns = [
        path('authors/', views.AuthorList.as_view()),
        # path('authors/posts/', views.PostList.as_view()),
        path('authors/<uuid:author_id>/posts/', views.PostList.as_view()),
        path('authors/<uuid:author_id>/posts/create-post/', views.CreatePost.as_view()),
        path('authors/<uuid:author_id>/posts/<uuid:post_id>/', views.PostDetail.as_view()),


        path('authors/<uuid:author_id>/followers/', views.FollowersList.as_view()),
        path('authors/<uuid:author_id>/followers/<uuid:follower_id>/', views.FollowersDetails.as_view()),

        path('authors/<uuid:author_id>/following/', views.FollowingList.as_view()),
        path('authors/<uuid:author_id>/friends/', views.FriendsList.as_view()),
        path('authors/<uuid:author_id>/requests/', views.RequestsList.as_view()),
        path('authors/<uuid:author_id>/requests/<uuid:request_follower_id>', views.RequestsList.as_view()),
]
