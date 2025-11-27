from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DR", _("Draft")
        SCHEDULED = "SC", _("Scheduled")
        PUBLISHED = "PU", _("Published")

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=200, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=2, choices=Status, default=Status.DRAFT)
    featured_image = models.ImageField(upload_to='media/images/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
        ]

    def save(self, *args, **kwargs):
        """
        Auto-generate unique slug based on title
        Auto-update status based on published_at date
        """
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            count = 1
            while Article.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{count}"
                count += 1
            self.slug = unique_slug

        if self.status == Article.Status.SCHEDULED and self.published_at:
            if timezone.now() >= self.published_at:
                self.status = Article.Status.PUBLISHED
        
        super().save(*args, **kwargs)

    def is_published(self):
        """
        Check if article is actually publisjed (not just scheduled)
        """
        return (
            self.status == Article.Status.PUBLISHED and
            self.published_at and
            self.published_at <= timezone.now()
        )

    def __str__(self):
        return self.title    




