from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage

from blog.models import Article


def dashboard(request):
    if not request.user.is_authenticated:
        raise Http404("Page does not exist")
    
    ARTICLES_PER_PAGE = 15
    page_number = request.GET.get('page', 1)
    articles = Article.objects.all().order_by("-created_at")
    paginator = Paginator(articles, ARTICLES_PER_PAGE)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage as e:
        return render(request, 'blog/dashboard.html', {"message": str(e)})
    
    context = {
        "page_obj": page_obj,
        "STATUS": Article.Status,
    }

    return render(request, 'blog/dashboard.html', context)
