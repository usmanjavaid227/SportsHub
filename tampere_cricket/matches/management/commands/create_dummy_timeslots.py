from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from tampere_cricket.matches.models import TimeSlot
from tampere_cricket.grounds.models import Ground


class Command(BaseCommand):
    help = 'Create dummy time slots for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to create time slots for (default: 7)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Get or create a ground
        ground, created = Ground.objects.get_or_create(
            name="Test Cricket Ground",
            defaults={
                'location': 'Tampere, Finland',
                'capacity': 200,
                'facilities': 'Full cricket facilities with nets and practice area'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created ground: {ground.name}')
            )
        
        # Create time slots for the next N days
        today = date.today()
        time_slots_created = 0
        
        for day_offset in range(days):
            current_date = today + timedelta(days=day_offset)
            
            # Create time slots for each day (9 AM to 7 PM, 2-hour slots)
            time_slots = [
                {'start': '09:00', 'end': '11:00', 'price': 50.00},
                {'start': '11:00', 'end': '13:00', 'price': 60.00},
                {'start': '13:00', 'end': '15:00', 'price': 70.00},
                {'start': '15:00', 'end': '17:00', 'price': 80.00},
                {'start': '17:00', 'end': '19:00', 'price': 90.00},
            ]
            
            for slot in time_slots:
                # Check if slot already exists
                existing_slot = TimeSlot.objects.filter(
                    ground=ground,
                    date=current_date,
                    start_time=time.fromisoformat(slot['start'])
                ).first()
                
                if not existing_slot:
                    TimeSlot.objects.create(
                        ground=ground,
                        date=current_date,
                        start_time=time.fromisoformat(slot['start']),
                        end_time=time.fromisoformat(slot['end']),
                        price=slot['price'],
                        is_available=True
                    )
                    time_slots_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {time_slots_created} time slots for {days} days'
            )
        )
