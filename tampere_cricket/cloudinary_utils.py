"""
Cloudinary utility functions for handling image uploads and URLs
"""
import cloudinary
import cloudinary.uploader
import os
from django.conf import settings


def upload_to_cloudinary(file, folder="avatars"):
    """
    Upload a file to Cloudinary and return the public_id
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image"
        )
        return result['public_id']
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None


def get_cloudinary_url(public_id, transformations=None):
    """
    Get Cloudinary URL for a public_id
    """
    if not public_id:
        return None
    
    try:
        if transformations:
            url = cloudinary.utils.cloudinary_url(public_id, **transformations)[0]
        else:
            url = cloudinary.utils.cloudinary_url(public_id)[0]
        return url
    except Exception as e:
        print(f"Cloudinary URL error: {e}")
        return None


def is_cloudinary_enabled():
    """
    Check if Cloudinary is enabled
    """
    return os.getenv('USE_CLOUDINARY', 'False').lower() == 'true'
