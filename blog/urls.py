from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="index"),
    path("article/<str:article_slug>/", views.article, name="article"),
    path("article/<str:article_slug>/edit/", views.edit, name="edit"),
    path("drafts/<int:article_id>/", views.drafts, name="drafts"),
    path("drafts/<int:article_id>/autosave/", views.autosave, name="autosave"),
    path("write/", views.write, name="write"),
]
