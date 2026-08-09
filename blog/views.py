from django.shortcuts import render, get_object_or_404
from .models import Article, Video

# Create your views here.


def home(request):
    list_articles = Article.objects.all()
    context = {
        'liste_articles': list_articles
    }
    return render(request, 'index.html', context)


def detail(request, article_id):
    article = get_object_or_404(Article, id = article_id)
    category = article.category
    articles_en_relation = Article.objects.filter(category = category).exclude(id = article_id)[:3]
    context = {
        'article': article,
        'category': category,
        'articles_en_relation': articles_en_relation
    }
    return render(request, 'detail.html', context)


def videos(request):
    liste_videos = Video.objects.all()
    context = {
        'liste_videos': liste_videos
    }
    return render(request, 'videos.html', context)