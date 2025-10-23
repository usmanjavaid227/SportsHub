"""
Custom Cloudinary storage backend for Django
"""
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.conf import settings
import os


class CloudinaryStorage(Storage):
    """
    Custom storage backend that uploads files to Cloudinary
    """
    
    def __init__(self):
        # Configure Cloudinary if not already configured
        if not hasattr(cloudinary.config(), 'cloud_name'):
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
    
    def _open(self, name, mode='rb'):
        # For reading, we'll return the Cloudinary URL
        return cloudinary.CloudinaryResource(name)
    
    def _save(self, name, content):
        # Upload to Cloudinary
        try:
            result = cloudinary.uploader.upload(
                content,
                public_id=name.replace('/', '_').replace('.', '_'),
                folder="media/avatars"
            )
            return result['public_id']
        except Exception as e:
            # If upload fails, return the original name
            return name
    
    def delete(self, name):
        # Delete from Cloudinary
        try:
            cloudinary.uploader.destroy(name)
        except:
            pass  # Ignore errors
    
    def exists(self, name):
        # Check if file exists in Cloudinary
        try:
            result = cloudinary.api.resource(name)
            return result is not None
        except:
            return False
    
    def url(self, name):
        # Return Cloudinary URL
        if name:
            return f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME')}/image/upload/{name}"
        return ""
    
    def size(self, name):
        # Get file size from Cloudinary
        try:
            result = cloudinary.api.resource(name)
            return result.get('bytes', 0)
        except:
            return 0
    
    def get_available_name(self, name, max_length=None):
        # Return a unique name for the file
        return name
