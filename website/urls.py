from django.urls import path
from . import views
from .feeds import BlogFeed

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog, name='blog'),
    path('blog/feed/', BlogFeed(), name='blog_feed'),
    path('blog/<slug:slug>/', views.post_detail, name='post_detail'),
]
