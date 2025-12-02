from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("articles/<str:article_slug>/", views.articles, name="articles"),
    path("articles/<str:article_slug>/edit/", views.edit, name="edit"),
    path("drafts/<int:article_id>/", views.drafts, name="drafts"),
    path("autosave/", views.autosave, name="autosave"),
    path("images/upload/", views.upload_image, name="upload_image"),
    path("write/", views.write, name="write"),
    path("search/article/", views.search_article, name="search_article"),
]
