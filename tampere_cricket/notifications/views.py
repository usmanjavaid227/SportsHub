from django.shortcuts import render
from .models import Notification


def notifications_list(request):
    """List all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})
