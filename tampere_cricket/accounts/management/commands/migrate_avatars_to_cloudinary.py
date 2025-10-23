"""
Management command to migrate existing avatars to Cloudinary
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from tampere_cricket.accounts.models import User
from tampere_cricket.cloudinary_utils import upload_to_cloudinary, is_cloudinary_enabled
import os


class Command(BaseCommand):
    help = 'Migrate existing avatars to Cloudinary'

    def handle(self, *args, **options):
        if not is_cloudinary_enabled():
            self.stdout.write(
                self.style.ERROR('Cloudinary is not enabled. Set USE_CLOUDINARY=True')
            )
            return

        users_with_avatars = User.objects.filter(avatar__isnull=False).exclude(avatar='')
        
        self.stdout.write(f'Found {users_with_avatars.count()} users with avatars')
        
        migrated_count = 0
        error_count = 0
        
        for user in users_with_avatars:
            try:
                # Check if avatar is already a Cloudinary URL
                if user.avatar.url.startswith('https://res.cloudinary.com/'):
                    self.stdout.write(f'User {user.username} already has Cloudinary avatar')
                    continue
                
                # Read the avatar file
                if user.avatar and hasattr(user.avatar, 'read'):
                    avatar_file = user.avatar.read()
                    
                    # Upload to Cloudinary
                    public_id = upload_to_cloudinary(
                        ContentFile(avatar_file),
                        folder=f"avatars/{user.id}"
                    )
                    
                    if public_id:
                        # Update the user's avatar field with Cloudinary public_id
                        user.avatar = public_id
                        user.save()
                        migrated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Migrated avatar for {user.username}')
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'Failed to upload avatar for {user.username}')
                        )
                        
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error migrating {user.username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Migration complete: {migrated_count} migrated, {error_count} errors'
            )
        )
