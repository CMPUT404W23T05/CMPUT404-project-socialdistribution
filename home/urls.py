from django.urls import path, include

from home import views, social_views

app_name = 'home'
urlpatterns = [
        path('posts/', views.BrowsePosts.as_view()),
        path('authors/', views.AuthorList.as_view()),
        path('authors/<uuid:author_id>/', views.AuthorDetail.as_view()),
        path('authors/<uuid:author_id>/posts/', views.PostList.as_view()),
        path('authors/<uuid:author_id>/posts/<uuid:post_id>/', views.PostDetail.as_view()),

        path('authors/<uuid:author_id>/posts/<uuid:post_id>/image', views.ImageView.as_view()),
        path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments', views.CommentList.as_view()),
        path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>', views.CommentDetail.as_view()),
        
        
        path('authors/<uuid:author_id>/followers/', social_views.FollowersList.as_view()),
        path('authors/<uuid:author_id>/followers/<uuid:follower_id>/', social_views.FollowersDetails.as_view()),

        path('authors/<uuid:author_id>/following/', social_views.FollowingList.as_view()),
        path('authors/<uuid:author_id>/friends/', social_views.FriendsList.as_view()),

        path('authors/<uuid:author_id>/posts/<uuid:post_id>/likes/', views.PostLikes.as_view()),
        path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes/', views.CommentLikes.as_view()),
        path('authors/<uuid:author_id>/liked/', views.LikedList.as_view()),

        path('authors/<uuid:author_id>/inbox/', views.InboxDetails.as_view()),

        path('remotes/<path:url>', views.RemoteApiKey.as_view()),
        path('key', views.GenericKey.as_view()),

        path('authors/<uuid:author_id>/remote-requests/', views.RemoteRequestsList.as_view())
]
