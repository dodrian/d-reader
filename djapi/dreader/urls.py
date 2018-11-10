from django.urls import path
from . import views
from django.http import JsonResponse


urlpatterns = [
  path('', views.index, name='index'),
  path('<str:user>/<slug:feedslug>', views.feed, name='feed'),
  path('feed/<int:feed_id>/addSource/', views.addFeedSource, name='add-feedsource'),
  path('<str:user>/', views.allFeeds, name='all-feeds'),
  path('post/<str:post_id>/read', views.readPost, name='read-post')
]
