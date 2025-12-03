from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("articles/<str:article_slug>/", views.articles, name="articles"),
    path("articles/<str:article_slug>/edit/", views.edit, name="edit"),
    path("articles/<int:article_id>/delete/", views.article_delete, name="article_delete"),
    path("drafts/<int:article_id>/", views.drafts, name="drafts"),
    path("write/", views.write, name="write"),
    path("topics/", views.all_topics, name="all_topics"),
    path("topics/<str:topic_slug>/", views.topic, name="topic"),

    # API ROUTES
    path("api/images/upload/", views.upload_image, name="upload_image"),
    path("api/articles/autosave/", views.autosave, name="autosave_article"),
    path("api/search/articles/", views.search_article, name="search_article"),
]
