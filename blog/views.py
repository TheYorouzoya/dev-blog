import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage

from .models import Article
from .forms import ArticleForm, ArticleImageForm


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


def dashboard(request):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")
    
    ARTICLES_PER_PAGE = 15
    page_number = request.GET.get('page', 1)
    articles = Article.objects.all()
    paginator = Paginator(articles, ARTICLES_PER_PAGE)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage as e:
        return render(request, 'blog/dashboard.html', {"message": str(e)})
    return render(request, 'blog/dashboard.html', {"page_obj": page_obj})


def article(request, article_slug):
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
            return redirect('blog:article', article_slug=updated_article.slug)
    elif request.method == 'DELETE':
        article.delete()
        return redirect('index')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'blog/write.html', {
        "form": form,
        "is_edit": not is_draft,
        "article_id": article.id,
    })


def edit(request, article_slug):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")
    
    article = get_object_or_404(Article, slug=article_slug)
    return _article_editor(request, article, is_draft=False)


def draft(request, article_id):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")

    article = get_object_or_404(Article, pk=article_id, status=Article.Status.DRAFT)
    return _article_editor(request, article, is_draft=True)


def autosave(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    
    data = json.loads(request.body)
    article_id = data['id']
    
    if not article_id:
        return JsonResponse({"error": "Missing article id"}, status=400)

    article = get_object_or_404(Article, pk=article_id)
    
    updated_title = data['title']
    updated_content = data['content']
    updated_excerpt = data['excerpt']

    article.title = updated_title
    article.content = updated_content
    article.excerpt = updated_excerpt

    article.save()

    return JsonResponse({"message": "Draft autosaved"})


def write(request):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")
    
    article_draft = Article(author=request.user)
    article_draft.status = Article.Status.DRAFT
    article_draft.save()
    
    return redirect('blog:draft', article_id=article_draft.id)


def upload_image(request):
    if request.method != 'POST':
        return JsonResponse({"message:" "Method not allowed"}, status=405)
    
    form = ArticleImageForm(request.POST, request.FILES)
    if form.is_valid():
        saved_image = form.save()
        return JsonResponse({"message": "Image uploaded successfully!", "url": saved_image.image.url})

    return JsonResponse({"message": "Image upload failed."})