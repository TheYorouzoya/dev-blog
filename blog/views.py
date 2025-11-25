from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from .models import Article

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


def article(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    return render(request, "blog/article.html", {"article": article})