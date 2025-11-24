from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(upload_to='uploads/images/', blank=True)

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
        Auto-update status based on published_at date
        """
        if self.status == 'scheduled' and self.published_at:
            if timezone.now() >= self.published_at:
                self.status = 'published'
        super().save(*args, **kwargs)

    def is_published(self):
        """
        Check if article is actually publisjed (not just scheduled)
        """
        return (
            self.status == 'published' and
            self.published_at and
            self.published_at <= timezone.now()
        )
    




