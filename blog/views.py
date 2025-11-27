from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage

from .models import Article
from .forms import ArticleForm

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
    if not request.user.is_authenticated:
        article = get_object_or_404(Article, slug=article_slug, status=Article.Status.PUBLISHED)
    else:
        article = get_object_or_404(Article, slug=article_slug)
    return render(request, "blog/article.html", {"article": article})


def edit(request, article_slug):
    if not request.user.is_authenticated:
        return Http404("Page does not exist")
    
    article = get_object_or_404(Article, slug=article_slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save()
            return redirect('blog:article', article_slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'blog/write.html', { "form": form, "is_edit": True})



def write(request):
    if not request.user.is_authenticated:
        return Http404("Page does not exist")
    
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()

            return redirect('blog:article', article_slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, "blog/write.html", { "form": form, "is_edit": False })