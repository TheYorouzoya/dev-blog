import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from blog.models import Article
from blog.forms import ArticleImageForm, TopicForm


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


@require_POST
def upload_image(request):
    form = ArticleImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({
            "success": False,
            "message": "Image upload failed.",
            "errors": form.errors,
        }, status=400)

    saved_image = form.save()
    return JsonResponse({
        "success": True,
        "message": "Image uploaded successfully!", 
        "url": saved_image.image.url,
        "id": saved_image.id,
    }, status=201)


@require_GET
def search_article(request):
    RESULTS_LIMIT = 5
    query = request.GET.get("q")
    query = query.strip()

    if not query:
        return JsonResponse({
            "results": []
        }, status=200)
    
    qSet = Article.objects.filter(status=Article.Status.PUBLISHED) \
                            .filter(title__icontains=query) \
                            .order_by('title')[:RESULTS_LIMIT]
    
    return JsonResponse({
        "results": [article.search_serialize() for article in qSet]
    }, status=200)


@require_POST
def topics_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    topic_form = TopicForm(request.POST)
    if topic_form.is_valid():
        new_topic = topic_form.save()
        return JsonResponse(
            {
                "message": "Topic addess successfully",
                "topic": new_topic.serialize(),
            }
            , status=201)
    return JsonResponse(
        {
            "message": "Invalid form data",
            "errors": topic_form.errors,
        }
        , status=400)