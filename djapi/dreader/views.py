from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Feed, FeedSource, Post
import feedparser
from datetime import datetime
from time import localtime
from pprint import pformat
import json
# Create your views here.
def index(request):
    return HttpResponse("Hello, world.  This is the d-reader API")

def feed(request, user, feedslug):
    try:
        feed = Feed.objects.get(slug=feedslug, user__username=user)
    except Feed.DoesNotExist:
        return JsonResponse({})

    return JsonResponse(feed.getUnreadPosts())

# functional programming is fun, but inefficient
def allFeeds_ineff(request, user):
    feeds = Feed.objects.filter(user__username=user)
    return HttpResponse(pformat(list(map(lambda f: f.getUnreadPosts(), feeds)), safe=False))

# This view is much much faster with fewer DB hits
def allFeeds(request, user):
    feeds = Feed.objects.filter(user__username='default').select_related('user').prefetch_related('feedsource_set__post_set')
    json = []
    for feed in feeds:
        json_feed = { 'id': feed.id, 'name': feed.name, 'sources': [], 'posts': []}
        for fs in feed.feedsource_set.all():
            source, posts = fs.getPosts()
            json_feed['sources'].append(source)
            json_feed['posts'].extend(posts)
        json.append(json_feed)
    return JsonResponse(json, safe=False)

def readPost(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.read=True
    post.save()
    return JsonResponse(post.json())

# Need to find a workable django-cookie session solution
@csrf_exempt
def addFeedSource(request, feed_id):
    request_string = request.body.decode()
    json_body = json.loads(request_string)
    link = json_body['link']
    feed = get_object_or_404(Feed, id=feed_id)

    fs = feed.feedsource_set.create(
        link = link,
        title = "Loading...",
        description = "Loading...",
    )
    source, posts = fs.getPosts()
    return JsonResponse({'source': source, 'posts': posts})
