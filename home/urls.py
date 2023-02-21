from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
        path('', views.login, name='login'),
        path('home/', views.index, name='index'),
]
