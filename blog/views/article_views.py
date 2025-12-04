import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_POST
from django.utils import timezone

from blog.models import Article, ArticleImage
from blog.forms import ArticleForm, TopicForm


def index(request):
    ARTICLES_PER_PAGE = 10
    page_number = request.GET.get('page', 1)
    articles = Article.objects.filter(status=Article.Status.PUBLISHED)
    paginator = Paginator(articles, ARTICLES_PER_PAGE)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage as e:
        return render(request, 'blog/index.html', {"message": str(e)})
    return render(request, 'blog/index.html', {"page_obj": page_obj})


def articles(request, article_slug):
    if not request.user.is_authenticated:
        article = get_object_or_404(Article, slug=article_slug, status=Article.Status.PUBLISHED)
    else:
        article = get_object_or_404(Article, slug=article_slug)

    return render(request, "blog/article.html", {"article": article})


def _article_editor(request, article, is_draft=False):
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save()
            updated_article.published_at = timezone.now()
            updated_article.save()
            
            json_ids = form.cleaned_data.get('image_ids') or "[]"
            image_ids = set(json.loads(json_ids))

            ArticleImage.objects.filter(article=article) \
                                .exclude(id__in=image_ids).delete()

            return redirect('blog:articles', article_slug=updated_article.slug)
    else:
        form = ArticleForm(instance=article)
    
    context = {
        "form": form,
        "topic_form": TopicForm(),
        "is_edit": not is_draft,
        "article_id": article.id,
        "STATUS": Article.Status,
    }

    return render(request, 'blog/write.html', context)


def edit(request, article_slug):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")
    
    article = get_object_or_404(Article, slug=article_slug)
    return _article_editor(request, article, is_draft=False)


def drafts(request, article_id):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")

    article = get_object_or_404(Article, pk=article_id, status=Article.Status.DRAFT)
    return _article_editor(request, article, is_draft=True)


def write(request):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")
    
    article_draft = Article(author=request.user)
    article_draft.status = Article.Status.DRAFT
    article_draft.save()
    
    return redirect('blog:drafts', article_id=article_draft.id)


@require_POST
def article_delete(request, article_id):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")

    article = get_object_or_404(Article, pk=article_id)

    article.delete()

    return redirect('blog:dashboard')
