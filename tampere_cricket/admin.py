from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_moderation(request):
    """Admin moderation page"""
    return render(request, 'admin_moderation.html')
