from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count

from blog.models import Article, Topic


def all_topics(request):
    all_topics = Topic.objects.annotate(article_count=Count('article'))

    context = {
        "topics": all_topics,
    }

    return render(request, 'blog/topics.html', context)


def topic(request, topic_slug):
    ARTICLES_PER_PAGE = 10
    topic = get_object_or_404(Topic, slug=topic_slug)
    
    page_num = request.GET.get('page', 1)
    articles = Article.objects.filter(topic=topic)
    paginator = Paginator(articles, ARTICLES_PER_PAGE)

    top_articles = Article.objects.filter(topic=topic).order_by('-views')[:5]

    try:
        page_obj = paginator.page(page_num)
    except EmptyPage as e:
        context = {
            "message": str(e),
            "topic": topic,
            "sidebar": {
                "top_articles": top_articles,
            },
        }
        return render(request, 'blog/index.html', context)

    context = {
        "page_obj": page_obj,
        "topic": topic,
        "sidebar": {
            "top_articles": top_articles,
        },
    }
    return render(request, 'blog/index.html', context)

