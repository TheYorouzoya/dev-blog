from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Topic, Tag, ArticleImage


# ---------- Helper: thumbnail renderer ----------
def render_thumbnail(image_field, size=60):
    if not image_field:
        return "-"
    return format_html(
        "<img src='{}' style='width: {}px; height: auto; border-radius:4px;'/>",
        image_field.url,
        size
    )


# ---------- INLINE IMAGE ADMIN (for Article edit page) ----------
class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    readonly_fields = ("thumbnail",)
    fields = ("image", "thumbnail",)
    
    def thumbnail(self, obj):
        return render_thumbnail(obj.image, size=80)
    thumbnail.short_description = "Preview"


# ---------- TOPIC ADMIN ----------
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description_short")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def description_short(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_short.short_description = "Description"


# ---------- TAG ADMIN ----------
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# ---------- ARTICLE ADMIN ----------
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "topic",
        "author",
        "published_at",
        "views",
        "featured_thumbnail",
    )
    list_filter = ("status", "topic", "tags", "author")
    search_fields = ("title", "content", "excerpt")
    date_hierarchy = "published_at"
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ArticleImageInline]

    actions = ["publish_selected", "unpublish_selected"]

    def featured_thumbnail(self, obj):
        return render_thumbnail(obj.featured_image, size=60)
    featured_thumbnail.short_description = "Thumbnail"

    def publish_selected(self, request, queryset):
        queryset.update(status=Article.Status.PUBLISHED)
    publish_selected.short_description = "Publish selected articles"

    def unpublish_selected(self, request, queryset):
        queryset.update(status=Article.Status.DRAFT)
    unpublish_selected.short_description = "Unpublish selected articles"


# ---------- ARTICLE IMAGE ADMIN (standalone) ----------
@admin.register(ArticleImage)
class ArticleImageAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "image_name", "image_preview")
    list_filter = ("article",)
    search_fields = ("article__title", "image")
    readonly_fields = ("image_preview",)

    def image_name(self, obj):
        return obj.image.name.split("/")[-1]
    image_name.short_description = "Filename"

    def image_preview(self, obj):
        return render_thumbnail(obj.image, size=120)
    image_preview.short_description = "Preview"

