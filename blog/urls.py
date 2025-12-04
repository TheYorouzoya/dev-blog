from django.urls import path, include

from .views import article_views, dashboard_views, topic_views

app_name = "blog"
urlpatterns = [
    path("", article_views.index, name="index"),
    path("dashboard/", dashboard_views.dashboard, name="dashboard"),

    # Articles
    path("articles/<str:article_slug>/", article_views.articles, name="articles"),
    path("articles/<str:article_slug>/edit/", article_views.edit, name="edit"),
    path("articles/<int:article_id>/delete/", article_views.article_delete, name="article_delete"),

    # Drafts
    path("drafts/<int:article_id>/", article_views.drafts, name="drafts"),
    path("write/", article_views.write, name="write"),
    
    # Topics
    path("topics/", topic_views.all_topics, name="all_topics"),
    path("topics/<str:topic_slug>/", topic_views.topic, name="topic"),

    # API ROUTES
    path("api/", include('blog.api_urls')),
]
