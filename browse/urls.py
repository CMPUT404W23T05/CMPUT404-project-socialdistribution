from django.urls import path
from . import views

#Browse inbox, stream, and public posts
urlpatterns = [
    path('', views.public, name='browse'),
]
