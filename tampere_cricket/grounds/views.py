from django.shortcuts import render, get_object_or_404
from .models import Ground


def ground_detail(request, ground_id):
    """Ground detail view"""
    try:
        ground = get_object_or_404(Ground, id=ground_id)
        return render(request, 'grounds/detail.html', {'ground': ground})
    except Exception as e:
        # For debugging - remove in production
        from django.http import HttpResponse
        return HttpResponse(f"Error: {str(e)}")
