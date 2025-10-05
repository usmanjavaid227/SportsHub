from django.shortcuts import render, get_object_or_404
from .models import Ground


def grounds_list(request):
    """List all grounds"""
    grounds = Ground.objects.filter(is_available=True)
    return render(request, 'grounds.html', {'grounds': grounds})


def ground_detail(request, ground_id):
    """Ground detail view"""
    ground = get_object_or_404(Ground, id=ground_id)
    return render(request, 'grounds/detail.html', {'ground': ground})
