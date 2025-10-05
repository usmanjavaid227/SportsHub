"""
URL configuration for tampere_cricket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from tampere_cricket.matches.views import ChallengeViewSet, challenges_list, challenge_detail, challenge_accept
from tampere_cricket.accounts.views import public_profile_view, signup, profile, custom_login, custom_logout
from tampere_cricket.grounds.views import grounds_list
from tampere_cricket.news.views import news_list
from tampere_cricket import pages
from tampere_cricket import admin as project_admin

router = DefaultRouter()
router.register(r'challenges', ChallengeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Authentication URLs
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', signup, name='register'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Password Change URLs (for logged-in users)
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url=reverse_lazy('password_change_done')
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    
    # App URLs
    path('accounts/', include('tampere_cricket.accounts.urls')),
    path('matches/', include('tampere_cricket.matches.urls')),
    path('grounds/', include('tampere_cricket.grounds.urls')),
    path('news/', include('tampere_cricket.news.urls')),
    path('notifications/', include('tampere_cricket.notifications.urls')),
    
    # Main pages
    path('', pages.home, name='home'),
    path('leaderboard/', pages.leaderboard, name='leaderboard'),
    path('contact/', pages.contact, name='contact'),
    
    # Direct URLs for templates
    path('grounds/', grounds_list, name='grounds'),
    path('news/', news_list, name='news'),
    
    # Profile URLs
    path('profile/', profile, name='profile'),
    path('profile/<int:user_id>/', public_profile_view, name='public_profile'),
    
    # Admin
    path('admin-moderation/', project_admin.admin_moderation, name='admin_moderation'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)