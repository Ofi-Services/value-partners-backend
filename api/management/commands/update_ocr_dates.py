from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import OCRInvoiceItem
import random

class Command(BaseCommand):
    help = 'Updates created_at dates for OCRInvoiceItem records with a range of dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to spread the dates across'
        )

    def handle(self, *args, **options):
        days = options['days']
        items = OCRInvoiceItem.objects.all()
        total_items = items.count()
        
        if total_items == 0:
            self.stdout.write(self.style.WARNING('No OCRInvoiceItem records found'))
            return

        # Calculate the time interval between items
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        time_interval = (end_date - start_date) / total_items

        self.stdout.write(f'Updating {total_items} records with dates from {start_date} to {end_date}')

        # Update each record with a random time within its interval
        for i, item in enumerate(items):
            base_time = start_date + (time_interval * i)
            # Add some randomness to the time (up to 80% of the interval)
            random_offset = timedelta(
                seconds=random.randint(0, int(time_interval.total_seconds() * 0.8))
            )
            item.created_at = base_time + random_offset
            item.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {total_items} records')) 