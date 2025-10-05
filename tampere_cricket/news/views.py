from django.shortcuts import render, get_object_or_404
from .models import News


def news_list(request):
    """List all published news"""
    news = News.objects.filter(published=True).order_by('-published_at')
    return render(request, 'news/list.html', {'news': news})


def news_detail(request, slug):
    """Display individual news article"""
    article = get_object_or_404(News, slug=slug, published=True)
    return render(request, 'news/detail.html', {'article': article})
