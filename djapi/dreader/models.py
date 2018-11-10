from django.db import models
from django.contrib.auth.models import User
import feedparser
from datetime import datetime
from time import localtime
# Create your models here.


class Feed(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(allow_unicode="true")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def getUnreadPosts(self):
        jsonfeed = {
            'name': self.name,
        }
        sources = []
        posts = []
        for source in self.feedsource_set.all():
            sources.append(source.link)
            source.reloadPosts()
            posts.extend(source.getUnreadPosts())
        jsonfeed['urls'] = sources
        jsonfeed['posts'] = posts
        return jsonfeed

    def getUnreadPostsEff(self):
        jsonfeed = {
            'name': self.name,
        }
        sources = []
        posts = []
        for source in self.feedsource_set.all():
            sources.append(source.link)
            source.reloadPosts_eff()
            posts.extend(source.getUnreadPosts())
        jsonfeed['urls'] = sources
        jsonfeed['posts'] = posts
        return jsonfeed

    class Meta:
        unique_together = (("slug", "user"),)


class FeedSource(models.Model):
    link = models.URLField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def getPosts(self):
        rss = feedparser.parse(self.link)
        posts_toread = []
        try:
            source = {'id': self.id, 'title': rss.feed.title, 'url': self.link }
            if self.title != rss.feed.title or self.description != rss.feed.description:
                self.title = rss.feed.title
                self.description = rss.feed.description
                self.save()
            guids = [e.guid for e in rss.entries]
            posts = self.post_set.filter(guid__in=guids)
            for entry in rss.entries:
                post = next(iter([post for post in posts if post.guid == entry.guid]), None)
                if post is None:
                    post = self.post_set.create(
                        link=entry.link,
                        title=entry.title,
                        description=entry.description,
                        guid=entry.guid,
                        read=False,
                        date=datetime(*getattr(entry, 'published_parsed', localtime())[0:6]),
                    )
                else:
                    if not all([getattr(post, x) == getattr(entry, x) for x in ['link','title','description','guid'] ]):
                        post.link = entry.link
                        post.title = entry.title
                        post.description = entry.description
                        if(hasattr(entry, 'published_parsed')):
                            post.date = datetime(*entry.published_parsed[0:6])
                        post.save()
                if not post.read:
                    posts_toread.append(post.json())
        except: # Error loading feed
            return {'id': self.id, 'url': self.link}, []
        return source, posts_toread

    def getUnreadPosts(self):
        return list(self.post_set.filter(read=False).values())


    class Meta:
        unique_together = (("feed", "link"),)


class Post(models.Model):
    feed = models.ForeignKey(FeedSource, on_delete=models.CASCADE)
    link = models.URLField()
    guid = models.CharField(max_length=300)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    read = models.BooleanField(default=False)

    def json(self):
        return {
            'id': self.id,
            'link': self.link,
            'guid': self.guid,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'read': self.read,
        }

    class Meta:
        unique_together = (("feed", "link"),)
