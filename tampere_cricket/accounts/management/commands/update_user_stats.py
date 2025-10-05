from django.core.management.base import BaseCommand
from tampere_cricket.accounts.models import Profile, User


class Command(BaseCommand):
    help = 'Update statistics for all users based on their completed matches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Update statistics for a specific user ID only',
        )

    def handle(self, *args, **options):
        if options['user_id']:
            try:
                user = User.objects.get(id=options['user_id'])
                profile, created = Profile.objects.get_or_create(user=user)
                stats = profile.update_statistics()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated statistics for user {user.username}: {stats}'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {options["user_id"]} not found')
                )
        else:
            # Update all users
            updated_count = 0
            for user in User.objects.all():
                profile, created = Profile.objects.get_or_create(user=user)
                stats = profile.update_statistics()
                updated_count += 1
                self.stdout.write(f'Updated {user.username}: {stats}')

            self.stdout.write(
                self.style.SUCCESS(f'Updated statistics for {updated_count} users')
            )
