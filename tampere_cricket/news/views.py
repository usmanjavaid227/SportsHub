from django.shortcuts import render, get_object_or_404
from .models import News, NewsCategory


def news_list(request):
    """List all published news with category filtering"""
    # Get filter parameters
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Get all published news
    news = News.objects.filter(published=True).order_by('-published_at')
    
    # Apply category filter
    if category_slug:
        news = news.filter(category__slug=category_slug)
    
    # Apply search filter
    if search_query:
        news = news.filter(title__icontains=search_query)
    
    # Get all categories for filter
    categories = NewsCategory.objects.all()
    
    # Get current category
    current_category = None
    if category_slug:
        current_category = NewsCategory.objects.filter(slug=category_slug).first()
    
    context = {
        'news': news,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
    }
    
    return render(request, 'news.html', context)


def news_detail(request, slug):
    """Display individual news article"""
    article = get_object_or_404(News, slug=slug, published=True)
    return render(request, 'news/detail.html', {'article': article})
