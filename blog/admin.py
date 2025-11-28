from django.contrib import admin

from .models import Article, Topic, Tag, ArticleImage

class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "status", "published_at"]

admin.site.register(Article, ArticleAdmin)
admin.site.register(Topic)
admin.site.register(Tag)
admin.site.register(ArticleImage)

