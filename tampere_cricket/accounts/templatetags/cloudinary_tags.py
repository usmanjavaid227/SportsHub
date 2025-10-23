"""
Template tags for Cloudinary integration
"""
from django import template
from django.conf import settings
import os

register = template.Library()


@register.filter
def cloudinary_url(value):
    """
    Convert avatar field to Cloudinary URL
    """
    if not value:
        return None
    
    # If it's already a Cloudinary URL, return as is
    if str(value).startswith('https://res.cloudinary.com/'):
        return str(value)
    
    # If Cloudinary is enabled, construct the URL
    if os.getenv('USE_CLOUDINARY', 'False').lower() == 'true':
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        if cloud_name:
            return f"https://res.cloudinary.com/{cloud_name}/image/upload/{value}"
    
    # Fallback to original value
    return str(value)
