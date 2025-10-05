from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tampere_cricket.news.models import News
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy news articles for testing'

    def handle(self, *args, **options):
        # Get or create an admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tamperecricket.fi',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.username}')
            )

        # Create dummy news articles
        dummy_news = [
            {
                'title': 'New Season of Single Wicket Cricket in Tampere Starts Soon!',
                'excerpt': 'Get ready for fresh challenges, improved ratings, and more grounds. The new season brings exciting updates to the Tampere cricket community.',
                'content': '''The Tampere cricket community is buzzing with excitement as we prepare for the upcoming season of Single Wicket Cricket. This year promises to be bigger and better than ever before!

**What's New This Season:**
- Enhanced rating system for fairer matchups
- New cricket grounds added to our network
- Improved challenge tracking and statistics
- Community tournaments and special events

**Key Dates:**
- Season starts: March 15th, 2024
- Registration opens: March 1st, 2024
- Pre-season warm-up matches: March 10-14th, 2024

We're thrilled to see the continued growth of cricket in Tampere and look forward to another fantastic season of competitive play. Whether you're a seasoned player or new to the sport, there's something for everyone in our community.

Stay tuned for more updates and don't forget to complete your profile to participate in challenges!''',
                'published': True,
                'published_at': timezone.now() - timedelta(days=2)
            },
            {
                'title': 'More Cricket Grounds Added to SportsHub Network',
                'excerpt': 'We are expanding available venues to make matches easier to arrange. Three new high-quality cricket grounds have been added to our network.',
                'content': '''Great news for all cricket enthusiasts in Tampere! We're excited to announce the addition of three new cricket grounds to the SportsHub network, making it even easier to find and book matches.

**New Grounds Added:**
1. **Tampere Sports Center** - Full-size pitch with excellent facilities
2. **Kaleva Cricket Ground** - Central location with parking available
3. **Hervanta Sports Complex** - Modern facilities with changing rooms

**Ground Features:**
- Well-maintained pitches suitable for all skill levels
- Parking facilities at all locations
- Changing rooms and equipment storage
- Easy booking through our platform

These additions bring our total number of available grounds to 8, ensuring that players across Tampere have convenient access to quality cricket facilities. Each ground has been carefully selected for its quality and accessibility.

**How to Book:**
Simply log into your SportsHub account, create a challenge, and select your preferred ground from the updated list. All grounds are available for booking 7 days a week.

We're committed to continuously improving the cricket experience in Tampere, and these new grounds are just the beginning of our expansion plans.''',
                'published': True,
                'published_at': timezone.now() - timedelta(days=5)
            },
            {
                'title': 'Community Spotlight: Meet Our Top Performers',
                'excerpt': 'Meet top performers and contributors from the Tampere cricket scene. This month we highlight outstanding players and their achievements.',
                'content': '''Welcome to our first Community Spotlight feature! This month, we're celebrating the outstanding players and contributors who make the Tampere cricket community so special.

**Player of the Month: Alex Thompson**
Alex has been a standout performer this season, with an impressive win rate of 85% across 20 matches. His dedication to the sport and positive attitude make him a true ambassador for cricket in Tampere.

**Rising Star: Maria Rodriguez**
Maria joined our community just three months ago and has already made a significant impact. Her rapid improvement and sportsmanship have earned her recognition from fellow players.

**Community Contributor: David Chen**
David has been instrumental in organizing community events and helping new players get started. His efforts have helped grow our community significantly.

**Achievement Highlights:**
- 150+ matches played this month across all players
- 95% player satisfaction rating
- 25 new players joined the community
- 3 community tournaments organized

**Upcoming Events:**
- Monthly community meetup: First Saturday of each month
- Skills workshop: Every other Sunday
- New player orientation: Every Tuesday

We're incredibly proud of our community and the positive impact cricket has had on bringing people together in Tampere. Thank you to all our players for making this such a wonderful community to be part of!

Stay tuned for more spotlights and community features in the coming months.''',
                'published': True,
                'published_at': timezone.now() - timedelta(days=7)
            }
        ]

        created_count = 0
        for news_data in dummy_news:
            news, created = News.objects.get_or_create(
                title=news_data['title'],
                defaults={
                    'author': admin_user,
                    'excerpt': news_data['excerpt'],
                    'content': news_data['content'],
                    'published': news_data['published'],
                    'published_at': news_data['published_at']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created news: {news.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'News already exists: {news.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} dummy news articles')
        )
