from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='published', published_at__lte=timezone.now())


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.CharField(max_length=300, blank=True, help_text='Optional short introduction for the blog list.')
    body = models.TextField(help_text='Write plain text. Separate paragraphs with a blank line; HTML is displayed as text.')
    category = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text='Leave blank to publish immediately, or choose a future date to schedule.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def summary(self):
        return self.excerpt or Truncator(self.body).chars(220)

    def get_absolute_url(self):
        return reverse('website:post_detail', kwargs={'slug': self.slug})


class ContactThrottle(models.Model):
    # Store a keyed hash and a counter, never the address or message itself.
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)
