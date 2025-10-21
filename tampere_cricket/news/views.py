from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import News, NewsCategory


def news_list(request):
    """List all published highlights with category filtering and pagination"""
    # Get filter parameters
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Get all published highlights that are not older than 1 month
    one_month_ago = timezone.now() - timedelta(days=30)
    news = News.objects.filter(
        published=True,
        created_at__gte=one_month_ago
    ).order_by('-published_at')
    
    # Apply category filter
    if category_slug:
        news = news.filter(category__slug=category_slug)
    
    # Apply search filter
    if search_query:
        news = news.filter(title__icontains=search_query)
    
    # Paginate results (6 per page)
    paginator = Paginator(news, 6)
    try:
        news_page = paginator.page(page)
    except:
        news_page = paginator.page(1)
    
    # Get all categories for filter
    categories = NewsCategory.objects.all()
    
    # Get current category
    current_category = None
    if category_slug:
        current_category = NewsCategory.objects.filter(slug=category_slug).first()
    
    context = {
        'news': news_page,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
        'paginator': paginator,
        'has_next': news_page.has_next(),
        'next_page': news_page.next_page_number() if news_page.has_next() else None,
    }
    
    return render(request, 'highlights.html', context)


def news_detail(request, slug):
    """Display individual highlights article"""
    article = get_object_or_404(News, slug=slug, published=True)
    return render(request, 'highlights/detail.html', {'article': article})
