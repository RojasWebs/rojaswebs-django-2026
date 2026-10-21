from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


class BlogFeed(Feed):
    title = 'RojasWebs Blog'
    description = 'Notes on web development, Django, and building real projects.'

    def link(self):
        return reverse('website:blog')

    def items(self):
        return Post.objects.published()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_pubdate(self, item):
        return item.published_at
